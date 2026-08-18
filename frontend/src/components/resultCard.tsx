import {
    CheckCircle2,
    Clock3,
    Package,
    ShieldCheck,
    TicketCheck,
    XCircle,
  } from "lucide-react";
  
  import type {
    StructuredResult,
  } from "../utils/messageResult";
  
  
  interface ResultCardProps {
    result: StructuredResult;
  }
  
  
  function ResultCard({
    result,
  }: ResultCardProps) {
  
    const normalizedStatus =
      result.status?.toLowerCase() ?? "";
  
  
    const isApproved =
      normalizedStatus.includes("approved") ||
      normalizedStatus.includes("completed") ||
      normalizedStatus.includes("delivered");
  
  
    const isRejected =
      normalizedStatus.includes("rejected") ||
      normalizedStatus.includes("failed");
  
  
    const isPending =
      normalizedStatus.includes("pending");
  
  
    function getIcon() {
      if (isApproved) {
        return <CheckCircle2 size={19} />;
      }
  
      if (isRejected) {
        return <XCircle size={19} />;
      }
  
      if (isPending) {
        return <Clock3 size={19} />;
      }
  
      if (result.kind === "ticket") {
        return <TicketCheck size={19} />;
      }
  
      if (result.kind === "escalation") {
        return <ShieldCheck size={19} />;
      }
  
      return <Package size={19} />;
    }

    function formatStatus(status: string) {
      return status
        .replace(/_/g, " ")
        .replace(/\b\w/g, (letter) =>
          letter.toUpperCase()
        );
    }
  
  
    function getStatusClasses() {
      if (isApproved) {
        return "bg-emerald-50 text-emerald-700";
      }
  
      if (isRejected) {
        return "bg-red-50 text-red-700";
      }
  
      if (isPending) {
        return "bg-amber-50 text-amber-700";
      }
  
      return "bg-zinc-100 text-zinc-600";
    }
  
  
    return (
      <div
        className="
          mb-4 overflow-hidden
          rounded-2xl
          border border-zinc-200
          bg-white
          shadow-sm
        "
      >
  
        {/* HEADER */}
        <div
          className="
            flex items-center justify-between
            gap-4
            border-b border-zinc-100
            px-5 py-4
          "
        >
  
          <div className="flex items-center gap-3">
  
            <div
              className="
                flex h-9 w-9
                items-center justify-center
                rounded-xl
                bg-zinc-950
                text-white
              "
            >
              {getIcon()}
            </div>
  
  
            <div>
              <div
                className="
                  text-sm font-semibold
                  text-zinc-900
                "
              >
                {result.title}
              </div>
  
              <div
                className="
                  mt-0.5 text-xs
                  text-zinc-500
                "
              >
                AI Support Agent
              </div>
            </div>
  
          </div>
  
  
          {result.status && (
            <span
              className={`
                rounded-full
                px-3 py-1
                text-xs font-medium
                ${getStatusClasses()}
              `}
            >
              {result.status}
            </span>
          )}
  
        </div>
  
  
        {/* DETAILS */}
        <div
          className="
            grid grid-cols-1
            gap-px bg-zinc-100
            sm:grid-cols-2
          "
        >
          {result.fields.map((field) => (
            <div
              key={`${field.label}-${field.value}`}
              className="
                bg-white
                px-5 py-3.5
              "
            >
              <div
                className="
                  mb-1
                  text-[11px]
                  font-medium uppercase
                  tracking-wide
                  text-zinc-400
                "
              >
                {field.label}
              </div>
  
              <div
                className="
                  break-words
                  font-mono
                  text-sm font-medium
                  text-zinc-800
                "
              >
                {field.value}
              </div>
            </div>
          ))}
        </div>
  
      </div>
    );
  }
  
  
  export default ResultCard;