export interface Conversation {
    conversation_id: string;
    title: string;
    updated_at: string | null;
  }
  
  export interface Message {
    id: string;
    role: "user" | "assistant";
    content: string;
    created_at: string;
  }
  
  export interface ConversationMessagesResponse {
    conversation_id: string;
    messages: Message[];
  }
  export interface ChatResponse {
    conversation_id: string;
    reply: string;
    status: "completed" | "pending_human_review";
    requires_human_review: boolean;
  
    data: {
      refund_id?: string;
      refund_status?: string;
      [key: string]: unknown;
    };
  }
  
  
  export interface RefundReviewResponse {
    conversation_id: string;
    refund_id: string;
    reply: string;
    status: "completed";
    requires_human_review: boolean;
  
    data: {
      refund_status?: string;
      [key: string]: unknown;
    };
  }