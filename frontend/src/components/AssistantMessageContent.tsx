import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import ResultCard from "./resultCard";

import {
  parseStructuredResult,
} from "../utils/messageResult";


interface AssistantMessageContentProps {
  content: string;
}


function AssistantMessageContent({
  content,
}: AssistantMessageContentProps) {

  const result =
    parseStructuredResult(content);

  const body =
    result?.body || content;


  return (
    <>
      {result && (
        <ResultCard result={result} />
      )}

      {body && (
        <div
          className="
            assistant-markdown
            text-sm leading-7
            text-zinc-800
          "
        >
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
          >
            {body}
          </ReactMarkdown>
        </div>
      )}
    </>
  );
}


export default AssistantMessageContent;