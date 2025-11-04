// Mock data for chats
export const mockChats = [
  {
    id: 1,
    name: "John Doe",
    avatar: "",
    lastMessage: "Hey, how are you?",
    timestamp: "2m ago",
    unread: 2,
    online: true,
  },
  {
    id: 2,
    name: "Jane Smith",
    avatar: "",
    lastMessage: "Can you send me the files?",
    timestamp: "1h ago",
    unread: 0,
    online: true,
  },
  {
    id: 3,
    name: "Mike Johnson",
    avatar: "",
    lastMessage: "Thanks for your help!",
    timestamp: "3h ago",
    unread: 0,
    online: false,
  },
  {
    id: 4,
    name: "Sarah Williams",
    avatar: "",
    lastMessage: "See you tomorrow!",
    timestamp: "1d ago",
    unread: 1,
    online: false,
  },
  {
    id: 5,
    name: "Tom Brown",
    avatar: "",
    lastMessage: "Let's schedule a meeting",
    timestamp: "2d ago",
    unread: 0,
    online: false,
  },
];

// Mock messages for selected chat
export const mockMessages = [
  {
    id: 1,
    senderId: 1,
    text: "Hey, how are you?",
    timestamp: "10:30 AM",
    isMine: false,
  },
  {
    id: 2,
    senderId: "me",
    text: "I'm good! How about you?",
    timestamp: "10:32 AM",
    isMine: true,
  },
  {
    id: 3,
    senderId: 1,
    text: "Doing great! Working on the project",
    timestamp: "10:33 AM",
    isMine: false,
  },
  {
    id: 4,
    senderId: "me",
    text: "That's awesome! Need any help?",
    timestamp: "10:35 AM",
    isMine: true,
  },
  {
    id: 5,
    senderId: 1,
    text: "Actually yes, could you review the code?",
    timestamp: "10:36 AM",
    isMine: false,
  },
];
