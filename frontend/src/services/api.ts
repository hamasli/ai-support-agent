import type {
    ChatResponse,
    Conversation,
    ConversationMessagesResponse,
  } from "../types/chat";
  
  
  const API_BASE_URL = "http://localhost:8001";
  
  
  export async function getConversations(): Promise<Conversation[]> {
    const response = await fetch(
      `${API_BASE_URL}/conversations`
    );
  
    if (!response.ok) {
      throw new Error(
        "Failed to load conversations."
      );
    }
  
    return response.json();
  }
  
  
  export async function getConversationMessages(
    conversationId: string
  ): Promise<ConversationMessagesResponse> {
    const response = await fetch(
      `${API_BASE_URL}/conversations/${conversationId}/messages`
    );
  
    if (!response.ok) {
      throw new Error(
        "Failed to load conversation."
      );
    }
  
    return response.json();
  }
  
  
  export async function sendChatMessage(
    message: string,
    conversationId?: string
  ): Promise<ChatResponse> {
    const response = await fetch(
      `${API_BASE_URL}/chat`,
      {
        method: "POST",
  
        headers: {
          "Content-Type": "application/json",
        },
  
        body: JSON.stringify({
          message,
          conversation_id:
            conversationId ?? null,
        }),
      }
    );
  
    if (!response.ok) {
      const error = await response.json();
  
      throw new Error(
        error.detail ??
          "Failed to send message."
      );
    }
  
    return response.json();
  }