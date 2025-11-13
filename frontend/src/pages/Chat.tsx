import { AgentChat } from "@/components/AgentChat";

const Chat = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex flex-col">
      <div className="flex-1 overflow-hidden">
        <AgentChat />
      </div>
    </div>
  );
};

export default Chat;
