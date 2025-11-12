import { Book, Globe } from "lucide-react";
import { ToolOption } from "./types";

export const toolOptions: ToolOption[] = [
  // Existing tools...
  {
    value: "arxiv",
    label: "Arxiv",
    description: "Search academic papers",
    icon: Book,
  },
  {
    value: "wikipedia",
    label: "Wikipedia",
    description: "Search encyclopedia articles",
    icon: Globe,
  },
];
