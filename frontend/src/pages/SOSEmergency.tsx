import { useState } from "react";
import { AlertTriangle, Plus, Trash2, Send, MapPin, User, Phone } from "lucide-react";
import { MainLayout } from "@/components/layout/MainLayout";
import { PageHeader } from "@/components/common/PageHeader";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";

interface Contact { id: string; name: string; phone: string; selected: boolean; }

export default function SOSEmergency() {
  const [userName, setUserName] = useState("");
  const [area, setArea] = useState("");
  const [mapsLink, setMapsLink] = useState("");
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [newName, setNewName] = useState("");
  const [newPhone, setNewPhone] = useState("");

  const addContact = () => {
    if (newName && newPhone) {
      setContacts([...contacts, { id: Date.now().toString(), name: newName, phone: newPhone, selected: true }]);
      setNewName(""); setNewPhone("");
    }
  };

  const toggleContact = (id: string) => setContacts(contacts.map(c => c.id === id ? { ...c, selected: !c.selected } : c));
  const removeContact = (id: string) => setContacts(contacts.filter(c => c.id !== id));

  const generateMessage = () => {
    return `🚨 EMERGENCY ALERT 🚨\n\nThis is ${userName || "someone"} and I need immediate help!\n\n📍 Location: ${area || "Unknown"}\n${mapsLink ? `🗺️ Maps: ${mapsLink}` : ""}\n\nPlease call me or send help immediately. This is an emergency.`;
  };

  const getWhatsAppLink = (phone: string) => {
    const cleanPhone = phone.replace(/\D/g, "");
    return `https://wa.me/${cleanPhone}?text=${encodeURIComponent(generateMessage())}`;
  };

  const selectedContacts = contacts.filter(c => c.selected);

  return (
    <MainLayout>
      <PageHeader title="SOS Emergency" subtitle="Prepare emergency alerts for trusted contacts" icon={<AlertTriangle className="w-6 h-6 text-destructive" />} />
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <Card className="border-destructive/30">
            <CardHeader><CardTitle className="flex items-center gap-2"><User className="w-5 h-5" />Your Details</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div><label className="text-sm font-medium">Your Name</label><Input value={userName} onChange={(e) => setUserName(e.target.value)} placeholder="Enter your name" /></div>
              <div><label className="text-sm font-medium">Area / Landmark</label><Input value={area} onChange={(e) => setArea(e.target.value)} placeholder="Near Metro Station, Sector 15..." /></div>
              <div><label className="text-sm font-medium flex items-center gap-2"><MapPin className="w-4 h-4" />Google Maps Link (optional)</label><Input value={mapsLink} onChange={(e) => setMapsLink(e.target.value)} placeholder="https://maps.google.com/..." /></div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2"><Phone className="w-5 h-5" />Trusted Contacts</CardTitle><CardDescription>Add contacts to alert in emergency</CardDescription></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Name" className="flex-1" />
                <Input value={newPhone} onChange={(e) => setNewPhone(e.target.value)} placeholder="+91..." className="flex-1" />
                <Button onClick={addContact} size="icon"><Plus className="w-4 h-4" /></Button>
              </div>
              {contacts.length === 0 ? <p className="text-sm text-muted-foreground text-center py-4">No contacts added yet</p> : (
                <div className="space-y-2">
                  {contacts.map((c) => (
                    <div key={c.id} className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                      <Checkbox checked={c.selected} onCheckedChange={() => toggleContact(c.id)} />
                      <div className="flex-1"><p className="font-medium text-sm">{c.name}</p><p className="text-xs text-muted-foreground">{c.phone}</p></div>
                      <Button variant="ghost" size="icon" onClick={() => removeContact(c.id)}><Trash2 className="w-4 h-4 text-destructive" /></Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <Card className="border-destructive/30 h-fit">
          <CardHeader><CardTitle className="text-destructive">Generate SOS</CardTitle><CardDescription>Click buttons below to open WhatsApp with pre-filled message</CardDescription></CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-lg bg-muted/50 text-sm whitespace-pre-wrap font-mono">{generateMessage()}</div>
            {selectedContacts.length === 0 ? <p className="text-sm text-muted-foreground text-center py-4">Select contacts above to generate SOS links</p> : (
              <div className="space-y-2">
                {selectedContacts.map((c) => (
                  <Button key={c.id} asChild className="w-full justify-start bg-green-600 hover:bg-green-700">
                    <a href={getWhatsAppLink(c.phone)} target="_blank" rel="noopener noreferrer"><Send className="w-4 h-4 mr-2" />Send to {c.name}</a>
                  </Button>
                ))}
              </div>
            )}
            <p className="text-xs text-muted-foreground text-center">Messages are NOT auto-sent. You'll confirm in WhatsApp before sending.</p>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}
