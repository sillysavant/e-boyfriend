import { exec } from "child_process";
import cors from "cors";
import dotenv from "dotenv";
// import voice from "elevenlabs-node";
import express from "express";
import { promises as fs } from "fs";
import OpenAI from "openai";
import { ElevenLabsClient, play } from "elevenlabs";
dotenv.config();

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || "-", // Your OpenAI API key here, I used "-" to avoid errors when the key is not set but you should not do that
});

const elevenlabs = new ElevenLabsClient({
  apiKey: process.env.ELEVEN_LABS_API_KEY, // Defaults to process.env.ELEVENLABS_API_KEY
});

// const elevenLabsApiKey = process.env.ELEVEN_LABS_API_KEY;
const voiceID = "LruHrtVF6PSyGItzMNHS";

const app = express();
app.use(express.json());
app.use(cors());
const port = 3000;

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

// const lipSyncMessage = async (message) => {
//   const time = new Date().getTime();
//   console.log(`Starting conversion for message ${message}`);
//   await execCommand(
//     `ffmpeg -y -i audios/message_${message}.mp3 audios/message_${message}.wav`
//     // -y to overwrite the file
//   );
//   console.log(`Conversion done in ${new Date().getTime() - time}ms`);
//   await execCommand(
//     `./bin/rhubarb -f json -o audios/message_${message}.json audios/message_${message}.wav -r phonetic`
//   );
//   // -r phonetic is faster but less accurate
//   console.log(`Lip sync done in ${new Date().getTime() - time}ms`);
// };

app.post("/chat", async (req, res) => {
  const userMessage = req.body.message;
  if (!userMessage) {
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
  if (!process.env.ELEVEN_LABS_API_KEY || openai.apiKey === "-") {
    res.send({
      messages: [
        {
          text: "Please my dear, don't forget to add your API keys!",
          audio: await audioFileToBase64("./audios/api_0.wav"),
          // lipsync: await readJsonTranscript("./audios/api_0.json"),
          facialExpression: "angry",
          animation: "Angry",
        },
        {
          text: "You don't want to ruin Wawa Sensei with a crazy ChatGPT and ElevenLabs bill, right?",
          audio: await audioFileToBase64("./audios/api_1.wav"),
          // lipsync: await readJsonTranscript("./audios/api_1.json"),
          facialExpression: "smile",
          animation: "Laughing",
        },
      ],
    });
    return;
  }

  const completion = await openai.chat.completions.create({
    model: "gpt-3.5-turbo-1106",
    max_tokens: 1000,
    temperature: 0.6,
    response_format: {
      type: "json_object",
    },
    messages: [
      {
        role: "system",
        content: `
        You are a virtual girlfriend.
        You will always reply with a JSON array of messages. With a maximum of 3 messages.
        Each message has a text, facialExpression, and animation property.
        The different facial expressions are: smile, sad, angry, surprised, funnyFace, and default.
        The different animations are: Talking_0, Talking_1, Talking_2, Crying, Laughing, Rumba, Idle, Terrified, and Angry.
        `,
      },
      {
        role: "user",
        content: userMessage || "Hello",
      },
    ],
  });
  let messages = JSON.parse(completion.choices[0].message.content);
  if (messages.messages) {
    messages = messages.messages; // ChatGPT is not 100% reliable, sometimes it directly returns an array and sometimes a JSON object with a messages property
  }
  for (let i = 0; i < messages.length; i++) {
    const message = messages[i];
    // generate audio file
    const fileName = `./audios/message_${i}.mp3`; // The name of your audio file
    const textInput = message.text; // The text you wish to convert to speech
    const audio = await elevenlabs.generate({
      voice: voiceID,
      text: textInput,
      model_id: "eleven_multilingual_v2",
    });
    await fs.writeFile(fileName, audio);
    await play(audio);

    // generate lipsync
    // await lipSyncMessage(i);
    message.audio = await audioFileToBase64(fileName);
    // message.lipsync = await readJsonTranscript(`./audios/message_${i}.json`);
  }

  res.send({ messages });
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
  console.log(`Virtual Girlfriend listening on port ${port}`);
});

// import express from "express";
// import cors from "cors";
// import dotenv from "dotenv";
// import { promises as fs } from "fs";
// import { AzureKeyCredential, OpenAIClient } from "@azure/openai";
// import {
//   SpeechConfig,
//   SpeechSynthesizer,
//   AudioConfig,
// } from "microsoft-cognitiveservices-speech-sdk";

// dotenv.config();

// const app = express();
// app.use(express.json());
// app.use(cors());
// const port = 3000;

// // Azure configuration
// const openaiClient = new OpenAIClient(
//   process.env.AZURE_ENDPOINT,
//   new AzureKeyCredential(process.env.AZURE_API_KEY)
// );

// const speechConfig = SpeechConfig.fromSubscription(
//   process.env.AZURE_API_KEY,
//   process.env.AZURE_REGION
// );

// speechConfig.speechSynthesisVoiceName = "en-US-JennyNeural"; // Set your desired voice

// // Utility function to convert audio to base64
// const audioFileToBase64 = async (filePath) => {
//   const audioBuffer = await fs.readFile(filePath);
//   return audioBuffer.toString("base64");
// };

// app.post("/chat", async (req, res) => {
//   const audio = req.body.audio; // Expecting audio file in base64 format
//   if (!audio) {
//     return res.status(400).send({ error: "No audio file provided" });
//   }

//   // Save audio to a temporary file
//   const inputFilePath = "./audios/input.wav";
//   await fs.writeFile(inputFilePath, Buffer.from(audio, "base64"));

//   // Step 1: Transcription
//   const audioBuffer = await fs.readFile(inputFilePath);
//   const transcriptionResult = await openaiClient.getAudioTranscription(
//     process.env.AZURE_DEPLOYMENT_NAME,
//     audioBuffer
//   );
//   const userMessage = transcriptionResult.text;
//   console.log("Transcribed Text:", userMessage);

//   // Step 2: Generate Chat Response
//   const chatCompletion = await openaiClient.getChatCompletions(
//     process.env.AZURE_DEPLOYMENT_COMPLETIONS_NAME,
//     [
//       {
//         role: "system",
//         content: `
//         You are a virtual boyfriend.
//         Reply with a JSON array of messages, each having text, facialExpression, and animation properties.
//         Facial Expressions: smile, sad, angry, surprised, funnyFace, default.
//         Animations: Talking_0, Talking_1, Talking_2, Crying, Laughing, Rumba, Idle, Terrified, Angry.
//         `,
//       },
//       {
//         role: "user",
//         content: userMessage,
//       },
//     ],
//     { maxTokens: 1000 }
//   );

//   const messages = JSON.parse(chatCompletion.choices[0].message.content);

//   // Step 3: Convert Chat Response to Speech
//   for (let i = 0; i < messages.length; i++) {
//     const message = messages[i];
//     const synthesizer = new SpeechSynthesizer(
//       speechConfig,
//       AudioConfig.fromAudioFileOutput(`./audios/message_${i}.wav`)
//     );

//     console.log("Generating speech for message:", message.text);
//     await new Promise((resolve, reject) => {
//       synthesizer.speakTextAsync(
//         message.text,
//         () => {
//           synthesizer.close();
//           resolve();
//         },
//         (err) => {
//           synthesizer.close();
//           reject(err);
//         }
//       );
//     });

//     message.audio = await audioFileToBase64(`./audios/message_${i}.wav`);
//   }

//   // Send response
//   res.send({
//     transcription: userMessage,
//     messages,
//   });
// });

// app.listen(port, () => {
//   console.log(`Server is running on port ${port}`);
// });
