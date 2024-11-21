"use server";

import { AzureKeyCredential, OpenAIClient } from "@azure/openai";

export default async function transcripts(formData) {
  "use server";

  if (
    !process.env.AZURE_API_KEY ||
    !process.env.AZURE_ENDPOINT ||
    !process.env.AZURE_DEPLOYMENT_NAME
  ) {
    console.error("Azure credentials not set");
    return {
      sender: "",
      response: "Azure credentials not set in transcripts",
    };
  }

  const file = formData.get("audio");
  if (file.size === 0) {
    return {
      sender: "",
      response: "No audio file provided",
    };
  }

  try {
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
    return {transcribedText: result.text};
  } catch (error) {
    res.status(500).json({ error: "Failed to transcribe audio" });
  }
}