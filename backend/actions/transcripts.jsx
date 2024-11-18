"use server";

import { AzureKeyCredential, OpenAIClient } from "@azure/openai";

export default async function transcript(prevState, formData) {
  "use server";

  const id = Math.random().toString(36);

  console.log("PREVIOUS STATE:", prevState);

  if (
    !process.env.AZURE_API_KEY ||
    !process.env.AZURE_ENDPOINT ||
    !process.env.AZURE_DEPLOYMENT_NAME ||
    !process.env.AZURE_DEPLOYMENT_COMPLETIONS_NAME
  ) {
    console.error("Azure credentials not set");
    return {
      sender: "",
      response: "Azure credentials not set",
    };
  }

  const file = formData.get("audio");
  if (file.size === 0) {
    return {
      sender: "",
      response: "No audio file provided",
    };
  }

  console.log(">>", file);

  const arrayBuffer = await file.arrayBuffer();
  const audio = new Uint8Array(arrayBuffer);

  console.log("== Transcribe Audio Sample ==");

  const client = new OpenAIClient(
    process.env.AZURE_ENDPOINT,
    new AzureKeyCredential(process.env.AZURE_API_KEY)
  );

  const result = await client.getAudioTranscription(
    process.env.AZURE_DEPLOYMENT_NAME,
    audio
  );
  console.log(`Transcription: ${result.text}`);

  const messages = [
    {
      role: "system",
      content:
        "You are a helpful assistant. You will answer questions and reply 'I cannot answer that' if you don't know the answer.",
    },
    { role: "user", content: result.text },
  ];

  console.log(`Messages: ${messages.map((m) => m.content).join("\n")}`);

  const completions = await client.getChatCompletions(
    process.env.AZURE_DEPLOYMENT_COMPLETIONS_NAME,
    messages,
    { maxTokens: 128 }
  );

  console.log("chatbot: ", completions.choices[0].message?.content);

  const response = completions.choices[0].message?.content;

  console.log(prevState.sender, "+++", result.text);
  return {
    sender: result.text,
    response: response,
    id: id,
  };
}
