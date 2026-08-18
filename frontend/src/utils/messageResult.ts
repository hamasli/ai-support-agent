export type ResultKind =
  | "ticket"
  | "refund"
  | "order"
  | "escalation";

export interface ResultField {
  label: string;
  value: string;
}

export interface StructuredResult {
  kind: ResultKind;
  title: string;
  status?: string;
  fields: ResultField[];
  body: string;
}


function findId(
  content: string,
  prefix: string
): string | undefined {
  const regex = new RegExp(
    `\\b${prefix}-[A-Z0-9]+\\b`,
    "i"
  );

  return content.match(regex)?.[0];
}


function findLabelValue(
  content: string,
  labels: string[]
): string | undefined {
  const plain = content.replace(/\*\*/g, "");

  for (const label of labels) {
    const regex = new RegExp(
      `(?:^|\\n)\\s*(?:[-*]\\s*)?${label}\\s*:\\s*([^\\n]+)`,
      "i"
    );

    const match = plain.match(regex);

    if (match?.[1]) {
      return match[1].trim();
    }
  }

  return undefined;
}


function cleanBody(content: string): string {
  const structuredLine =
    /^\s*(?:[-*]\s*)?(?:\*\*)?(Ticket ID|Refund ID|Escalation ID|Order ID|Customer ID|Customer|Status|Reference)(?:\*\*)?\s*:/i;

  return content
    .split("\n")
    .filter(
      (line) => !structuredLine.test(line)
    )
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}


export function parseStructuredResult(
  content: string
): StructuredResult | null {

  const ticketId =
    findId(content, "TKT");

  const refundId =
    findId(content, "REF");

  const escalationId =
    findId(content, "ESC");

  const orderId =
    findId(content, "ORD");

  const customerId =
    findId(content, "CUST");

  const status =
    findLabelValue(content, ["Status"]);

    const hasStructuredSignal =
    Boolean(ticketId) ||
    Boolean(refundId) ||
    Boolean(escalationId) ||
    Boolean(
      orderId &&
      (
        status ||
        /order\s+(status|details)/i.test(content)
      )
    );
  
  if (!hasStructuredSignal) {
    return null;
  }

  let kind: ResultKind | null = null;
  let title = "";


  if (refundId) {
    kind = "refund";

    if (
      status?.toLowerCase().includes("approved")
    ) {
      title = "Refund Approved";
    } else if (
      status?.toLowerCase().includes("rejected")
    ) {
      title = "Refund Rejected";
    } else {
      title = "Refund Request";
    }

  } else if (ticketId) {
    kind = "ticket";
    title = "Support Ticket Created";

  } else if (escalationId) {
    kind = "escalation";
    title = "Support Escalation";

  } else if (orderId) {
    kind = "order";
    title = "Order Details";
  }


  if (!kind) {
    return null;
  }


  const fields: ResultField[] = [];


  if (ticketId) {
    fields.push({
      label: "Ticket ID",
      value: ticketId,
    });
  }

  if (refundId) {
    fields.push({
      label: "Refund ID",
      value: refundId,
    });
  }

  if (escalationId) {
    fields.push({
      label: "Escalation ID",
      value: escalationId,
    });
  }

  if (orderId) {
    fields.push({
      label: "Order",
      value: orderId,
    });
  }

  if (customerId) {
    fields.push({
      label: "Customer",
      value: customerId,
    });
  }

  if (status) {
    fields.push({
      label: "Status",
      value: status,
    });
  }


  return {
    kind,
    title,
    status,
    fields,
    body: cleanBody(content),
  };
}