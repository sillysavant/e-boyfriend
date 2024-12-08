import { exec } from "child_process";
import cors from "cors";
import dotenv from "dotenv";
import express, { json } from "express";
import { promises as fs } from "fs";
import transcripts from "./actions/transcripts.js";
import generateCompletion from "./actions/generateCompletion.js";
import createAudioFileFromText from "./actions/createAudioFileFromText.js";
import multer from "multer";
import { ElevenLabsClient, play } from "elevenlabs";
dotenv.config();

const app = express();
app.use(express.json());
app.use(cors());
const port = 3000;
const upload = multer();
const elevenLabsApiKey = process.env.ELEVEN_LABS_API_KEY;

const elevenlabs = new ElevenLabsClient({
  apiKey: elevenLabsApiKey,
});

app.get("/", (req, res) => {
  res.send("Hello World!");
});

app.get("/voices", async (req, res) => {
  // res.send(await voice.getVoices(elevenlabs.apiKey));
  const response = await elevenlabs.voices.getAll(
    {},
    {
      maxRetries: 2,
    }
  );

  return res.send(response);
});

const execCommand = (command) => {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) reject(error);
      resolve(stdout);
    });
  });
};

const lipSyncMessage = async (message) => {
  const time = new Date().getTime();
  console.log(`Starting conversion for message ${message}`);
  await execCommand(
    `ffmpeg -y -i audios/message_${message}.mp3 audios/message_${message}.wav`
    // -y to overwrite the file
  );
  console.log(`Conversion done in ${new Date().getTime() - time}ms`);
  await execCommand(
    `.\\Rhubarb-Lip-Sync-1.13.0-Windows\\rhubarb.exe -f json -o audios/message_${message}.json audios/message_${message}.wav -r phonetic`
  );
  // -r phonetic is faster but less accurate
  console.log(`Lip sync done in ${new Date().getTime() - time}ms`);
};

const processMessages = async (messages) => {
  for (let i = 0; i < messages.length; ++i) {
    const message = messages[i];
    const textInput = message.text;
    const fileName = `audios/message_${i}.mp3`;
    // Generate the audio file
    const audioFileName = await createAudioFileFromText(textInput, fileName);
    // Convert the audio file to Base64
    message.audio = await audioFileToBase64(audioFileName);
    await lipSyncMessage(i);
    message.lipsync = await readJsonTranscript(`audios/message_${i}.json`);
  }
};

app.post("/chat", upload.single("audio"), async (req, res) => {
  let userMessage = req.body.message;
  const audioFile = req.file;

  if (!userMessage && !audioFile) {
    res.send({
      messages: [
        {
          text: "Hey dear... How was your day?",
          audio: await audioFileToBase64("audios/intro_0.wav"),
          // lipsync: await readJsonTranscript("audios/intro_0.json"),
          facialExpression: "smile",
          animation: "Talking_1",
        },
        {
          text: "I missed you so much... Please don't go for so long!",
          audio: await audioFileToBase64("audios/intro_1.wav"),
          // lipsync: await readJsonTranscript("audios/intro_1.json"),
          facialExpression: "sad",
          animation: "Crying",
        },
      ],
    });
    return;
  }

  if (!elevenLabsApiKey) {
    res.send({
      messages: [
        {
          text: "Please my dear, don't forget to add your API keys!",
          audio: await audioFileToBase64("audios/api_0.wav"),
          lipsync: await readJsonTranscript("audios/api_0.json"),
          facialExpression: "smile",
          animation: "Laughing",
        },
      ],
    });
    return;
  }

  if (audioFile) {
    const formData = new FormData();
    const audioBlob = new Blob([audioFile.buffer], { type: "audio/webm" });
    formData.append("audio", audioBlob, audioFile.originalname);

    const transcriptionResult = await transcripts(formData);
    if (transcriptionResult.error) {
      return res.status(400).send({
        error: transcriptionResult.error,
      });
    }
    userMessage = transcriptionResult.transcribedText;
    console.log("userMessage", userMessage);
  }
  // Generate completion from provided text (transcript or text in request)
  const completionResult = await generateCompletion(userMessage);
  if (completionResult.error) {
    return res.status(500).send({ error: completionResult.error });
  }
  // NOTE: vulnerable since gpt is not always returning json array (incomplete json)
  try {
    let messages = JSON.parse(completionResult.response);
    if (messages.messages) {
      messages = messages.messages;
    }
    console.log("messages", messages);
    await processMessages(messages);
    res.send({ messages });
  } catch (jsonError) {
    return res.status(500).send({ error: jsonError.message });
  }
});

const readJsonTranscript = async (file) => {
  const data = await fs.readFile(file, "utf8");
  return JSON.parse(data);
};

const audioFileToBase64 = async (file) => {
  const data = await fs.readFile(file);
  return data.toString("base64");
};

app.listen(port, () => {
  console.log(`Virtual Boyfriend listening on port ${port}`);
});
