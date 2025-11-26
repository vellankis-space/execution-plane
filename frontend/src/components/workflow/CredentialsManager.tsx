import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Key, Plus, Trash2, Eye, EyeOff, Edit } from "lucide-react";
import { toast } from "@/hooks/use-toast";

export interface Credential {
  id: string;
  name: string;
  type: string;
  data: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

const CREDENTIAL_TYPES = [
  {
    type: "api_key",
    label: "API Key",
    fields: [
      { name: "api_key", label: "API Key", type: "password", required: true },
      { name: "api_secret", label: "API Secret", type: "password", required: false },
    ],
  },
  {
    type: "oauth2",
    label: "OAuth2",
    fields: [
      { name: "client_id", label: "Client ID", type: "text", required: true },
      { name: "client_secret", label: "Client Secret", type: "password", required: true },
      { name: "access_token", label: "Access Token", type: "password", required: false },
      { name: "refresh_token", label: "Refresh Token", type: "password", required: false },
    ],
  },
  {
    type: "basic_auth",
    label: "Basic Auth",
    fields: [
      { name: "username", label: "Username", type: "text", required: true },
      { name: "password", label: "Password", type: "password", required: true },
    ],
  },
  {
    type: "database",
    label: "Database",
    fields: [
      { name: "host", label: "Host", type: "text", required: true },
      { name: "port", label: "Port", type: "number", required: true },
      { name: "database", label: "Database", type: "text", required: true },
      { name: "username", label: "Username", type: "text", required: true },
      { name: "password", label: "Password", type: "password", required: true },
    ],
  },
  {
    type: "smtp",
    label: "SMTP",
    fields: [
      { name: "host", label: "Host", type: "text", required: true },
      { name: "port", label: "Port", type: "number", required: true },
      { name: "username", label: "Username", type: "text", required: true },
      { name: "password", label: "Password", type: "password", required: true },
      { name: "secure", label: "Use TLS", type: "checkbox", required: false },
    ],
  },
  {
    type: "aws",
    label: "AWS",
    fields: [
      { name: "access_key_id", label: "Access Key ID", type: "text", required: true },
      { name: "secret_access_key", label: "Secret Access Key", type: "password", required: true },
      { name: "region", label: "Region", type: "text", required: true },
    ],
  },
];

export function CredentialsManager() {
  const [credentials, setCredentials] = useState<Credential[]>([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingCredential, setEditingCredential] = useState<Credential | null>(null);
  const [selectedType, setSelectedType] = useState("");
  const [credentialName, setCredentialName] = useState("");
  const [credentialData, setCredentialData] = useState<Record<string, any>>({});
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadCredentials();
  }, []);

  const loadCredentials = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/credentials");
      if (response.ok) {
        const data = await response.json();
        setCredentials(data);
      }
    } catch (error) {
      console.error("Error loading credentials:", error);
    }
  };

  const handleSaveCredential = async () => {
    if (!credentialName || !selectedType) {
      toast({
        title: "Validation Error",
        description: "Please provide name and type",
        variant: "destructive",
      });
      return;
    }

    const credentialType = CREDENTIAL_TYPES.find((t) => t.type === selectedType);
    if (!credentialType) return;

    // Validate required fields
    const missingFields = credentialType.fields
      .filter((f) => f.required && !credentialData[f.name])
      .map((f) => f.label);

    if (missingFields.length > 0) {
      toast({
        title: "Missing Required Fields",
        description: `Please provide: ${missingFields.join(", ")}`,
        variant: "destructive",
      });
      return;
    }

    try {
      const method = editingCredential ? "PUT" : "POST";
      const url = editingCredential
        ? `http://localhost:8000/api/v1/credentials/${editingCredential.id}`
        : "http://localhost:8000/api/v1/credentials";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: credentialName,
          type: selectedType,
          data: credentialData,
        }),
      });

      if (response.ok) {
        toast({
          title: "Success",
          description: `Credential ${editingCredential ? "updated" : "created"} successfully`,
        });
        setIsDialogOpen(false);
        resetForm();
        loadCredentials();
      } else {
        throw new Error("Failed to save credential");
      }
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.message || "Failed to save credential",
        variant: "destructive",
      });
    }
  };

  const handleDeleteCredential = async (id: string) => {
    if (!confirm("Are you sure you want to delete this credential?")) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/credentials/${id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        toast({ title: "Success", description: "Credential deleted" });
        loadCredentials();
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete credential",
        variant: "destructive",
      });
    }
  };

  const handleEditCredential = (credential: Credential) => {
    setEditingCredential(credential);
    setCredentialName(credential.name);
    setSelectedType(credential.type);
    setCredentialData(credential.data);
    setIsDialogOpen(true);
  };

  const resetForm = () => {
    setEditingCredential(null);
    setCredentialName("");
    setSelectedType("");
    setCredentialData({});
  };

  const toggleSecretVisibility = (fieldName: string) => {
    setShowSecrets((prev) => ({ ...prev, [fieldName]: !prev[fieldName] }));
  };

  const selectedCredentialType = CREDENTIAL_TYPES.find((t) => t.type === selectedType);

  return (
    <div className="space-y-4">
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogTrigger asChild>
          <Button onClick={resetForm} size="sm" className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Add Credential
          </Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>
              {editingCredential ? "Edit" : "Add"} Credential
            </DialogTitle>
            <DialogDescription>
              Store credentials securely for use in your workflows
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 mt-4">
            <div>
              <Label htmlFor="cred-name">Credential Name</Label>
              <Input
                id="cred-name"
                placeholder="e.g., Production API Key"
                value={credentialName}
                onChange={(e) => setCredentialName(e.target.value)}
                className="mt-1"
              />
            </div>

            <div>
              <Label htmlFor="cred-type">Credential Type</Label>
              <Select value={selectedType} onValueChange={setSelectedType}>
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select credential type" />
                </SelectTrigger>
                <SelectContent>
                  {CREDENTIAL_TYPES.map((type) => (
                    <SelectItem key={type.type} value={type.type}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedCredentialType && (
              <div className="space-y-3 pt-2 border-t">
                {selectedCredentialType.fields.map((field) => (
                  <div key={field.name}>
                    <Label htmlFor={field.name}>
                      {field.label}
                      {field.required && <span className="text-red-500 ml-1">*</span>}
                    </Label>
                    {field.type === "password" ? (
                      <div className="relative mt-1">
                        <Input
                          id={field.name}
                          type={showSecrets[field.name] ? "text" : "password"}
                          value={credentialData[field.name] || ""}
                          onChange={(e) =>
                            setCredentialData((prev) => ({
                              ...prev,
                              [field.name]: e.target.value,
                            }))
                          }
                          className="pr-10"
                        />
                        <Button
                          type="button"
                          variant="ghost"
                          size="icon"
                          className="absolute right-0 top-0 h-full"
                          onClick={() => toggleSecretVisibility(field.name)}
                        >
                          {showSecrets[field.name] ? (
                            <EyeOff className="w-4 h-4" />
                          ) : (
                            <Eye className="w-4 h-4" />
                          )}
                        </Button>
                      </div>
                    ) : field.type === "checkbox" ? (
                      <div className="flex items-center mt-2">
                        <input
                          id={field.name}
                          type="checkbox"
                          checked={credentialData[field.name] || false}
                          onChange={(e) =>
                            setCredentialData((prev) => ({
                              ...prev,
                              [field.name]: e.target.checked,
                            }))
                          }
                          className="w-4 h-4"
                        />
                      </div>
                    ) : (
                      <Input
                        id={field.name}
                        type={field.type}
                        value={credentialData[field.name] || ""}
                        onChange={(e) =>
                          setCredentialData((prev) => ({
                            ...prev,
                            [field.name]: e.target.value,
                          }))
                        }
                        className="mt-1"
                      />
                    )}
                  </div>
                ))}
              </div>
            )}

            <div className="flex justify-end gap-2 pt-4 border-t">
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSaveCredential}>
                {editingCredential ? "Update" : "Create"} Credential
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <div className="grid gap-4">
        {credentials.length === 0 ? (
          <Card className="p-8 text-center">
            <Key className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h4 className="font-semibold mb-2">No credentials yet</h4>
            <p className="text-sm text-muted-foreground mb-4">
              Add credentials to securely store API keys and connection details
            </p>
            <Button onClick={() => setIsDialogOpen(true)}>
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Credential
            </Button>
          </Card>
        ) : (
          credentials.map((cred) => (
            <Card key={cred.id} className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-md bg-primary/10">
                    <Key className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-semibold">{cred.name}</h4>
                      <Badge variant="secondary">
                        {CREDENTIAL_TYPES.find((t) => t.type === cred.type)?.label ||
                          cred.type}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Created {new Date(cred.createdAt).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handleEditCredential(cred)}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => handleDeleteCredential(cred.id)}
                  >
                    <Trash2 className="w-4 h-4 text-destructive" />
                  </Button>
                </div>
              </div>
            </Card>
          ))
        )}
      </div>
    </div >
  );
}
