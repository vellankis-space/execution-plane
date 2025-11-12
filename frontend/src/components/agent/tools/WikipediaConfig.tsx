import { Globe } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const WikipediaConfig = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="w-5 h-5" />
          Wikipedia Tool
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          Search Wikipedia encyclopedia articles. No configuration needed.
        </p>
      </CardContent>
    </Card>
  );
};

export default WikipediaConfig;
