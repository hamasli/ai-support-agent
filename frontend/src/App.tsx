
import {
  Bot,
  Check,
  CheckCircle2,
  Copy,
  Menu,
  MessageSquare,
  Plus,
  Send,
  ShieldCheck,
  XCircle,
  LoaderCircle,
} from "lucide-react";
import {
  useEffect,
  useRef,
  useState,
} from "react";

import type {
  FormEvent,
  KeyboardEvent,
} from "react";

import {
  getConversationMessages,
  getConversations,
  reviewRefund,
  sendChatMessage,
} from "./services/api";

import type {
  Conversation,
  Message,
} from "./types/chat";

import AssistantMessageContent
  from "./components/AssistantMessageContent";


function App() {

  
  const [conversations, setConversations] =
    useState<Conversation[]>([]);

  const [messages, setMessages] =
    useState<Message[]>([]);

  const [
    activeConversationId,
    setActiveConversationId,
  ] = useState<string | null>(null);

  const [input, setInput] = useState("");

  const [isSending, setIsSending] =
    useState(false);

  const [sidebarOpen, setSidebarOpen] =
    useState(true);


  const [error, setError] =
    useState<string | null>(null);

  const [copiedMessageId, setCopiedMessageId] =
    useState<string | null>(null);

  const messagesEndRef =
    useRef<HTMLDivElement | null>(null);

  const [pendingRefund, setPendingRefund] =
    useState<{
      refundId: string;
      conversationId: string;
    } | null>(null);

  // -------------------------------------------------------
  // LOAD CONVERSATIONS
  // -------------------------------------------------------

  async function loadConversations() {
    try {
      const data =
        await getConversations();

      setConversations(data);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to load conversations."
      );
    }
  }


  useEffect(() => {
    loadConversations();

    const savedConversationId =
      localStorage.getItem(
        "activeConversationId"
      );

    if (savedConversationId) {
      openConversation(
        savedConversationId
      );
    }
  }, []);


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isSending, pendingRefund]);


  const [
    isLoadingConversation,
    setIsLoadingConversation,
  ] = useState(false);

  // -------------------------------------------------------
  // OPEN OLD CONVERSATION
  // -------------------------------------------------------
  async function openConversation(
    conversationId: string
  ) {
    setError(null);
    setIsLoadingConversation(true);
  
    try {
      const data =
        await getConversationMessages(
          conversationId
        );
  
      setActiveConversationId(
        conversationId
      );
  
      localStorage.setItem(
        "activeConversationId",
        conversationId
      );
  
      setMessages(data.messages);
  
      if (data.pending_refund) {
        setPendingRefund({
          refundId:
            data.pending_refund.refund_id,
          conversationId:
            conversationId,
        });
      } else {
        setPendingRefund(null);
      }
  
      // Close sidebar automatically on phones
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      }
  
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to load conversation."
      );
    } finally {
      setIsLoadingConversation(false);
    }
  }


  // -------------------------------------------------------
  // NEW CHAT
  // -------------------------------------------------------

  function startNewChat() {
    setActiveConversationId(null);
    setMessages([]);
    
    setInput("");
    setError(null);
    setPendingRefund(null);

    localStorage.removeItem(
      "activeConversationId"
    );
    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
  }


  // -------------------------------------------------------
  // SEND MESSAGE
  // -------------------------------------------------------

  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault();

    const cleanMessage = input.trim();

    if (
      !cleanMessage ||
      isSending ||
      isLoadingConversation
    ) {
      return;
    }
    setError(null);
    const temporaryUserMessage: Message = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: cleanMessage,
      created_at:
        new Date().toISOString(),
    };

    setMessages((current) => [
      ...current,
      temporaryUserMessage,
    ]);

    setInput("");
    setIsSending(true);

    try {
      const result =
        await sendChatMessage(
          cleanMessage,
          activeConversationId ??
          undefined
        );
      if (
        result.status === "pending_human_review" &&
        result.requires_human_review &&
        result.data.refund_id
      ) {
        setPendingRefund({
          refundId: result.data.refund_id,
          conversationId:
            result.conversation_id,
        });
      }

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: result.reply,
        created_at:
          new Date().toISOString(),
      };

      setMessages((current) => [
        ...current,
        assistantMessage,
      ]);

      setActiveConversationId(
        result.conversation_id
      );

      localStorage.setItem(
        "activeConversationId",
        result.conversation_id
      );

      await loadConversations();
    }
    catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Something went wrong. Please try again."
      );
    } finally {
      setIsSending(false);
    }
  }
  function handleKeyDown(
    event: KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();

      event.currentTarget.form?.requestSubmit();
    }
  }
  function formatTime(date: string) {
    return new Date(date).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  const [isReviewing, setIsReviewing] =
    useState(false);

  async function copyMessage(
    messageId: string,
    content: string
  ) {
    await navigator.clipboard.writeText(content);

    setCopiedMessageId(messageId);

    setTimeout(() => {
      setCopiedMessageId(null);
    }, 1500);
  }
  async function handleRefundReview(
    approved: boolean
  ) {
    if (!pendingRefund || isReviewing) {
      return;
    }

    setError(null);
    setIsReviewing(true);

    try {
      const result = await reviewRefund(
        pendingRefund.refundId,
        pendingRefund.conversationId,
        approved
      );

      const reviewMessage: Message = {
        id: `review-${Date.now()}`,
        role: "assistant",
        content: result.reply,
        created_at:
          new Date().toISOString(),
      };

      setMessages((current) => [
        ...current,
        reviewMessage,
      ]);

      setPendingRefund(null);

      await loadConversations();
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to review refund."
      );
    } finally {
      setIsReviewing(false);
    }
  }
  return (
    <div className="flex h-screen overflow-hidden bg-white text-zinc-900">
      {sidebarOpen && (
  <button
    type="button"
    aria-label="Close sidebar"
    onClick={() => setSidebarOpen(false)}
    className="
      fixed inset-0 z-30
      bg-black/40
      md:hidden
    "
  />
)}
      {sidebarOpen && (
  <button
    type="button"
    aria-label="Close sidebar"
    onClick={() =>
      setSidebarOpen(false)
    }
    className="
      fixed inset-0 z-30
      bg-black/40
      md:hidden
    "
  />
)}
      {/* SIDEBAR */}
      <aside
  className={`
    fixed inset-y-0 left-0 z-40
    w-72 flex-shrink-0
    border-r border-zinc-800
    bg-zinc-950 text-white
    transition-all duration-300

    md:relative
    md:inset-auto
    md:z-auto

    ${
      sidebarOpen
        ? "translate-x-0 md:w-72"
        : `
          -translate-x-full
          md:w-0
          md:translate-x-0
          md:overflow-hidden
        `
    }
  `}
>
        <div className="flex h-full flex-col">

          <div className="p-4">
            <button
              onClick={startNewChat}
              className="
                flex w-full items-center gap-3
                rounded-xl border border-zinc-700
                px-4 py-3
                text-sm font-medium
                transition
                hover:bg-zinc-800
              "
            >
              <Plus size={18} />

              New conversation
            </button>
          </div>


          <div className="px-4 pb-2 text-xs font-medium uppercase tracking-wider text-zinc-500">
            Recent conversations
          </div>


          <div className="flex-1 overflow-y-auto px-2">

            {conversations.length === 0 ? (
              <div className="px-3 py-4 text-sm text-zinc-500">
                No conversations yet.
              </div>
            ) : (
              conversations.map(
                (conversation) => (
                  <button
                    key={
                      conversation.conversation_id
                    }
                    onClick={() =>
                      openConversation(
                        conversation.conversation_id
                      )
                    }
                    className={`
                      mb-1 flex w-full items-center
                      gap-3 rounded-lg
                      px-3 py-3 text-left
                      text-sm transition

                      ${activeConversationId ===
                        conversation.conversation_id
                        ? "bg-zinc-800 text-white"
                        : "text-zinc-300 hover:bg-zinc-900"
                      }
                    `}
                  >
                    <MessageSquare
                      size={16}
                      className="shrink-0"
                    />

                    <span className="truncate">
                      {conversation.title}
                    </span>
                  </button>
                )
              )
            )}
          </div>


          <div className="border-t border-zinc-800 p-4">
            <div className="flex items-center gap-3">
              <div className="
                flex h-9 w-9 items-center
                justify-center rounded-full
                bg-white text-zinc-900
              ">
                <Bot size={18} />
              </div>

              <div>
                <div className="text-sm font-medium">
                  AI Support Agent
                </div>

                <div className="text-xs text-zinc-500">
                  Online
                </div>
              </div>
            </div>
          </div>

        </div>
      </aside>


      {/* MAIN CHAT */}
      <main className="flex min-w-0 flex-1 flex-col">

        {/* HEADER */}
        <header className="
          flex h-16 items-center
          border-b border-zinc-200
          px-4
        ">
          <button
            onClick={() =>
              setSidebarOpen(
                (current) => !current
              )
            }
            className="
              rounded-lg p-2
              hover:bg-zinc-100
            "
          >
            <Menu size={20} />
          </button>

          <div className="ml-3">
            <h1 className="text-sm font-semibold">
              AI Support Agent
            </h1>

            <p className="text-xs text-zinc-500">
              Customer support assistant
            </p>
          </div>
        </header>


        {/* MESSAGES */}
        <section className="flex-1 overflow-y-auto">

        {isLoadingConversation ? (
  <div
    className="
      flex h-full
      items-center justify-center
    "
  >
    <div
      className="
        flex items-center gap-3
        text-sm text-zinc-500
      "
    >
      <LoaderCircle
        size={20}
        className="animate-spin"
      />

      Loading conversation...
    </div>
  </div>
) : messages.length === 0 ? ( (
            <div className="
              flex h-full items-center
              justify-center px-6
            ">
              <div className="max-w-xl text-center">

                <div className="
                  mx-auto mb-5 flex
                  h-14 w-14 items-center
                  justify-center rounded-2xl
                  bg-zinc-950 text-white
                ">
                  <Bot size={28} />
                </div>

                <h2 className="
                  mb-2 text-2xl
                  font-semibold tracking-tight
                ">
                  How can I help you?
                </h2>

                <p className="
                  text-sm leading-6
                  text-zinc-500
                ">
                  Ask about an order,
                  company policy, damaged item,
                  delivery, support request,
                  or refund.
                </p>

              </div>
            </div>
          )) : (
            <div className="
            mx-auto w-full max-w-3xl
            px-3 py-6
            sm:px-5 sm:py-8
            ">

              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`
      mb-8 flex
      ${message.role === "user"
                      ? "justify-end"
                      : "justify-start"
                    }
    `}
                >

                  {/* ASSISTANT ICON */}
                  {message.role === "assistant" && (
                    <div
                      className="
          mr-3 mt-1 flex
          h-8 w-8 shrink-0
          items-center justify-center
          rounded-lg bg-zinc-950
          text-white
        "
                    >
                      <Bot size={17} />
                    </div>
                  )}


                  <div
                    className={`
        group
        ${message.role === "user"
                        ? "max-w-[88%] max-w-[75%]"
                        :  "max-w-[94%] sm:max-w-[88%]"
                      }
      `}
                  >

                    {/* MESSAGE */}
                    {message.role === "user" ? (
                      <div
                        className="
            whitespace-pre-wrap
            rounded-2xl rounded-br-md
            bg-zinc-100
            px-4 py-2.5
            text-sm leading-6
          "
                      >
                        {message.content}
                      </div>
                    ) : (
                      <AssistantMessageContent
                        content={message.content}
                      />
                    )}


                    {/* MESSAGE ACTIONS */}
                    <div
                      className={`
          mt-2 flex items-center gap-2
          text-xs text-zinc-400

          ${message.role === "user"
                          ? "justify-end"
                          : "justify-start"
                        }
        `}
                    >

                      <span>
                        {formatTime(message.created_at)}
                      </span>


                      {message.role === "assistant" && (
                        <button
                          onClick={() =>
                            copyMessage(
                              message.id,
                              message.content
                            )
                          }
                          title="Copy response"
                          className="
              flex items-center gap-1
              rounded-md px-1.5 py-1
              transition
              hover:bg-zinc-100
              hover:text-zinc-700
            "
                        >
                          {copiedMessageId ===
                            message.id ? (
                            <>
                              <Check size={13} />
                              Copied
                            </>
                          ) : (
                            <>
                              <Copy size={13} />
                              Copy
                            </>
                          )}
                        </button>
                      )}

                    </div>

                  </div>
                </div>
              ))}

              {pendingRefund && (
                <div
                  className="
      mb-8 ml-11
      max-w-xl
      overflow-hidden
      rounded-2xl
      border border-amber-200
      bg-amber-50
    "
                >

                  <div
                    className="
        flex items-center gap-3
        border-b border-amber-200
        px-5 py-4
      "
                  >
                    <div
                      className="
          flex h-9 w-9
          items-center justify-center
          rounded-xl
          bg-amber-100
          text-amber-700
        "
                    >
                      <ShieldCheck size={19} />
                    </div>

                    <div>
                      <div className="font-semibold text-zinc-900">
                        Human Review Required
                      </div>

                      <div className="text-xs text-zinc-500">
                        Reviewer Mode
                      </div>
                    </div>
                  </div>


                  <div className="px-5 py-4">

                    <div className="mb-4 text-sm text-zinc-600">
                      This refund request is paused
                      until a human reviewer makes a
                      decision.
                    </div>


                    <div
                      className="
          mb-5 rounded-xl
          bg-white
          px-4 py-3
          text-sm
        "
                    >
                      <div className="text-xs text-zinc-500">
                        Refund ID
                      </div>

                      <div className="mt-1 font-mono font-medium text-zinc-900">
                        {pendingRefund.refundId}
                      </div>
                    </div>


                    <div className="flex gap-3">

                      <button
                        disabled={isReviewing}
                        onClick={() =>
                          handleRefundReview(false)
                        }
                        className="
            flex flex-1 items-center
            justify-center gap-2
            rounded-xl
            border border-red-200
            bg-white
            px-4 py-2.5
            text-sm font-medium
            text-red-700
            transition
            hover:bg-red-50
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
                      >
                        <XCircle size={17} />
                        Reject
                      </button>


                      <button
                        disabled={isReviewing}
                        onClick={() =>
                          handleRefundReview(true)
                        }
                        className="
            flex flex-1 items-center
            justify-center gap-2
            rounded-xl
            bg-zinc-950
            px-4 py-2.5
            text-sm font-medium
            text-white
            transition
            hover:bg-zinc-800
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
                      >
                        <CheckCircle2 size={17} />

                        {isReviewing
                          ? "Processing..."
                          : "Approve"}
                      </button>

                    </div>

                  </div>
                </div>
              )}
              

              {isSending && (
                <div className="flex items-center gap-3">

                  <div
                    className="
        flex h-8 w-8
        items-center justify-center
        rounded-lg bg-zinc-950
        text-white
      "
                  >
                    <Bot size={17} />
                  </div>


                  <div
                    className="
        flex items-center gap-1
        rounded-xl bg-zinc-100
        px-4 py-3
      "
                  >
                    <span className="thinking-dot" />
                    <span className="thinking-dot" />
                    <span className="thinking-dot" />
                  </div>

                </div>
              )}
              <div ref={messagesEndRef} />

            </div>
          )}

        </section>


        {/* INPUT */}
        <div className="
  border-t border-zinc-100
  bg-white
  px-3 pb-3 pt-3
  sm:px-4 sm:pb-5
">
          {error && (
            <div
              className="
      mx-auto mb-3 max-w-3xl
      rounded-xl border border-red-200
      bg-red-50
      px-4 py-3
      text-sm text-red-700
    "
            >
              {error}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="
              mx-auto flex
              max-w-3xl items-end
              gap-3 rounded-2xl
              border border-zinc-300
              bg-white
              p-2
              shadow-sm
              focus-within:border-zinc-400
            "
          >

            <textarea
              value={input}

              onChange={(event) =>
                setInput(
                  event.target.value
                )
              }
              onKeyDown={handleKeyDown}
              placeholder="Ask a support question..."
              rows={1}
              className="
                max-h-36 min-h-11
                flex-1 resize-none
                bg-transparent
                px-3 py-2.5
                text-sm outline-none
                placeholder:text-zinc-400

              "
            />


            <button
              type="submit"
              disabled={
                !input.trim() ||
                isSending ||
                isLoadingConversation
              }
              className="
                flex h-10 w-10
                items-center justify-center
                rounded-xl
                bg-zinc-950 text-white
                transition
                hover:bg-zinc-800
                disabled:cursor-not-allowed
                disabled:bg-zinc-300
              "
            >
              <Send size={17} />
            </button>

          </form>


          <p className="
            mx-auto mt-2
            max-w-3xl
            text-center text-[11px]
            text-zinc-400
          ">
            AI responses may require human
            review for certain actions.
          </p>

        </div>

      </main>

    </div>
  );
}


export default App;