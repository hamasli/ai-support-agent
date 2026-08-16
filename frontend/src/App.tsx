import {
  Bot,
  Menu,
  MessageSquare,
  Plus,
  Send,
} from "lucide-react";
import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  getConversationMessages,
  getConversations,
  sendChatMessage,
} from "./services/api";

import type {
  Conversation,
  Message,
} from "./types/chat";


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


  // -------------------------------------------------------
  // LOAD CONVERSATIONS
  // -------------------------------------------------------

  async function loadConversations() {
    try {
      const data =
        await getConversations();

      setConversations(data);
    } catch (error) {
      console.error(error);
    }
  }


  useEffect(() => {
    loadConversations();
  }, []);


  // -------------------------------------------------------
  // OPEN OLD CONVERSATION
  // -------------------------------------------------------

  async function openConversation(
    conversationId: string
  ) {
    try {
      const data =
        await getConversationMessages(
          conversationId
        );

      setActiveConversationId(
        conversationId
      );

      setMessages(data.messages);
    } catch (error) {
      console.error(error);
    }
  }


  // -------------------------------------------------------
  // NEW CHAT
  // -------------------------------------------------------

  function startNewChat() {
    setActiveConversationId(null);
    setMessages([]);
    setInput("");
  }


  // -------------------------------------------------------
  // SEND MESSAGE
  // -------------------------------------------------------

  async function handleSubmit(
    event: FormEvent
  ) {
    event.preventDefault();

    const cleanMessage = input.trim();

    if (!cleanMessage || isSending) {
      return;
    }

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

      await loadConversations();
    } catch (error) {
      console.error(error);
    } finally {
      setIsSending(false);
    }
  }


  return (
    <div className="flex h-screen overflow-hidden bg-white text-zinc-900">

      {/* SIDEBAR */}
      <aside
        className={`
          flex-shrink-0 border-r border-zinc-200
          bg-zinc-950 text-white
          transition-all duration-300
          ${
            sidebarOpen
              ? "w-72"
              : "w-0 overflow-hidden"
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

                      ${
                        activeConversationId ===
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

          {messages.length === 0 ? (
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
          ) : (
            <div className="
              mx-auto w-full max-w-3xl
              px-5 py-8
            ">

              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`
                    mb-7 flex
                    ${
                      message.role === "user"
                        ? "justify-end"
                        : "justify-start"
                    }
                  `}
                >

                  {message.role ===
                    "assistant" && (
                    <div className="
                      mr-3 mt-1 flex
                      h-8 w-8 shrink-0
                      items-center justify-center
                      rounded-lg bg-zinc-950
                      text-white
                    ">
                      <Bot size={17} />
                    </div>
                  )}


                  <div
                    className={`
                      max-w-[80%]
                      whitespace-pre-wrap
                      text-sm leading-6

                      ${
                        message.role ===
                        "user"
                          ? `
                            rounded-2xl
                            rounded-br-md
                            bg-zinc-100
                            px-4 py-2.5
                          `
                          : "py-1"
                      }
                    `}
                  >
                    {message.content}
                  </div>

                </div>
              ))}


              {isSending && (
                <div className="flex items-center gap-3 text-sm text-zinc-500">

                  <div className="
                    flex h-8 w-8
                    items-center justify-center
                    rounded-lg bg-zinc-950
                    text-white
                  ">
                    <Bot size={17} />
                  </div>

                  <span>
                    Thinking...
                  </span>

                </div>
              )}

            </div>
          )}

        </section>


        {/* INPUT */}
        <div className="
          border-t border-zinc-100
          bg-white px-4
          pb-5 pt-3
        ">

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
                isSending
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