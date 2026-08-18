
import type {
  ChatResponse,
  Conversation,
  ConversationMessagesResponse,
  RefundReviewResponse,
} from "../types/chat";
  
  
  const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8001";

  async function getErrorMessage(
    response: Response,
    fallback: string
  ): Promise<string> {
    try {
      const data = await response.json();
  
      if (typeof data.detail === "string") {
        return data.detail;
      }
  
      return fallback;
    } catch {
      return fallback;
    }
  }
  
  
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
        await getErrorMessage(
          response,
          "Unable to load conversations."
        )
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
      throw new Error(
        await getErrorMessage(
          response,
          "The AI service is currently unavailable. Please try again."
        )
      );
    }
  
    return response.json();
  }


  export async function reviewRefund(
    refundId: string,
    conversationId: string,
    approved: boolean
  ): Promise<RefundReviewResponse> {
  
    const response = await fetch(
      `${API_BASE_URL}/refunds/${refundId}/review`,
      {
        method: "POST",
  
        headers: {
          "Content-Type": "application/json",
        },
  
        body: JSON.stringify({
          conversation_id: conversationId,
          approved,
        }),
      }
    );
  
    if (!response.ok) {
      throw new Error(
        await getErrorMessage(
          response,
          "Unable to review this refund right now."
        )
      );
    }
  
    return response.json();
  }