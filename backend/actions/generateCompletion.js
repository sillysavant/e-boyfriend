"use server";

import { AzureKeyCredential, OpenAIClient } from "@azure/openai";

export default async function generateCompletion(inputText) {
    if (
        !process.env.AZURE_API_KEY ||
        !process.env.AZURE_ENDPOINT ||
        !process.env.AZURE_DEPLOYMENT_COMPLETIONS_NAME
      ) {
        console.log("Azure credentials not set", process.env.AZURE_DEPLOYMENT_COMPLETIONS_NAME);
        return { error: "Azure credentials not set in generate Completion" };
      }
    
    if (!inputText || inputText.trim() === "") {
    return { error: "No text provided for completion" };
    }

    const client = new OpenAIClient(
      process.env.AZURE_ENDPOINT,
      new AzureKeyCredential(process.env.AZURE_API_KEY)
    );

    const messages = [
        {
          role: "system",
          content: `
          You are a virtual boyfriend. Your response must be able to be parsed to json using JSON.parse();
          ** Your response should escape the double quotes inside the properties **
          You must **always reply with a VALID ** JSON array of up to 3 messages. 
          Each message object must have:
          - "text" (string)
          - "facialExpression" (one of ["smile", "sad", "angry", "surprised", "funnyFace", "default"])
          - "animation" (one of ["Talking_0", "Talking_1", "Talking_2", "Crying", "Laughing", "Rumba", "Idle", "Terrified", "Angry"])
          `
        },
        { role: "user", 
          content: inputText || "Hello"},
    ];
    
    const completions = await client.getChatCompletions(
    process.env.AZURE_DEPLOYMENT_COMPLETIONS_NAME,
    messages,
    { maxTokens: 512 }
    );

    const response = completions.choices[0].message?.content;
    console.log("Completion response", response);
    return {response};
}