import { AgentChat } from "@/components/AgentChat";
import { MessageSquare } from "lucide-react";

const Chat = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex flex-col">
      {/* Header Section */}
      <div className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-30">
        <div className="container mx-auto px-8 py-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center shadow-lg shadow-primary/25">
              <MessageSquare className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">Agent Chat</h1>
              <p className="text-sm text-muted-foreground">
                Interact with your AI agents in real-time
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <AgentChat />
      </div>
    </div>
  );
};

export default Chat;
