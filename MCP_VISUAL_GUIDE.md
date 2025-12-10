# 🎨 MCP AI - Visual Guide

## 📱 User Interface Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  🚀 DevOps Command Center                                            │
├──────────┬──────────────────────────────────────────────────────────┤
│          │  🤖 MCP AI                               [Notifications]  │
│ Sidebar  ├──────────────────────────────────────────────────────────┤
│          │                                                            │
│ [🏠]     │  ┌──────────────────┐  ┌─────────────────────────────┐  │
│ [✓] Tasks│  │  MCP Servers  [+]│  │ 🤖 MCP AI Assistant  [▼]    │  │
│ [🤖] MCP │  ├──────────────────┤  ├─────────────────────────────┤  │
│ [⚙] Set  │  │                  │  │                             │  │
│          │  │ 🔷 Prod ArgoCD   │  │  [Chat Messages Display]    │  │
│          │  │ ✓ Active         │  │                             │  │
│          │  │ [Edit][Test][Del]│  │  You: Show me apps         │  │
│          │  │                  │  │                             │  │
│          │  │ 🐙 GitHub Org    │  │  🤖: Here are the apps:    │  │
│          │  │ ✓ Active         │  │  - app1: Healthy ✓         │  │
│          │  │ [Edit][Test][Del]│  │  - app2: Degraded ⚠        │  │
│          │  │                  │  │                             │  │
│          │  │ ⚙️ Custom MCP    │  │                             │  │
│          │  │ ⚠ Pending        │  │                             │  │
│          │  │ [Edit][Test][Del]│  ├─────────────────────────────┤  │
│          │  │                  │  │ [Type message...]      [►]  │  │
│ [User]   │  │                  │  └─────────────────────────────┘  │
│ Sign Out │  └──────────────────┘                                    │
└──────────┴──────────────────────────────────────────────────────────┘
```

## 🎯 Key UI Elements

### Left Panel - MCP Server Management
```
┌─────────────────────────────┐
│  MCP Servers            [+] │  ← Add new MCP button
├─────────────────────────────┤
│ ┌───────────────────────┐   │
│ │ 🔷 Production ArgoCD  │   │  ← MCP Type Icon
│ │ Monitors all prod apps│   │  ← Description
│ │ ● Active              │   │  ← Status (Green = Active)
│ │ [Edit][Test][Delete]  │   │  ← Action buttons
│ └───────────────────────┘   │
│ ┌───────────────────────┐   │
│ │ 🐙 Company GitHub     │   │
│ │ Track PRs and issues  │   │
│ │ ● Active              │   │
│ │ [Edit][Test][Delete]  │   │
│ └───────────────────────┘   │
└─────────────────────────────┘
```

### Right Panel - Chat Interface
```
┌────────────────────────────────────┐
│ 🤖 MCP AI Assistant  [Select MCP▼] │  ← MCP Selector Dropdown
├────────────────────────────────────┤
│                                    │
│          ┌──────────────────┐     │
│          │ You: Show apps   │     │  ← User Message (Blue)
│          └──────────────────┘     │
│                                    │
│  ┌─────────────────────────────┐  │
│  │ 🤖 MCP Assistant:           │  │  ← Bot Response (Green)
│  │                             │  │
│  │ Applications:               │  │
│  │ - app1: ✓ Healthy, Synced  │  │
│  │ - app2: ⚠ Degraded         │  │
│  │ - app3: ✓ Healthy, Synced  │  │
│  └─────────────────────────────┘  │
│                                    │
│  System: Selected Production...   │  ← System Messages
│                                    │
├────────────────────────────────────┤
│ [Type your question here...]  [►] │  ← Input + Send
└────────────────────────────────────┘
```

## 🎨 Color Scheme

### Status Indicators
- 🟢 **Active** - Green (Server is connected and ready)
- 🟠 **Pending** - Orange (Waiting for configuration/test)
- 🔴 **Error** - Red (Connection failed or error state)
- ⚫ **Disabled** - Grey (Manually disabled)

### Message Bubbles
- 💙 **User Messages** - Blue background (#E3F2FD)
- 💚 **Assistant Messages** - Green background (#E8F5E9)
- ⚪ **System Messages** - Grey text, centered

## 📋 Add MCP Dialog

```
┌──────────────────────────────────────┐
│  Add MCP Server                      │
├──────────────────────────────────────┤
│                                      │
│  MCP Server Type *                   │
│  [🔷 ArgoCD MCP          ▼]         │
│                                      │
│  Name *                              │
│  [Production ArgoCD               ]  │
│                                      │
│  Description                         │
│  [Monitors all production apps    ]  │
│                                      │
│  ─────────────────────────────────   │
│                                      │
│  ArgoCD Configuration                │
│                                      │
│  Server URL *                        │
│  [https://argocd.company.com      ]  │
│                                      │
│  Namespace                           │
│  [argocd                          ]  │
│                                      │
│  ☑ Verify TLS/SSL certificates       │
│                                      │
│  Credentials                         │
│                                      │
│  API Token *                         │
│  [●●●●●●●●●●●●●●●●●●●]     [👁]     │
│                                      │
├──────────────────────────────────────┤
│              [Cancel]  [Save & Test] │
└──────────────────────────────────────┘
```

## 🔄 User Flow

### Adding an MCP Server
```
1. Click "MCP AI" in sidebar
   ↓
2. Click "+" button
   ↓
3. Select MCP Type (ArgoCD/GitHub/Custom)
   ↓
4. Fill in configuration:
   - Name
   - Server URL
   - Credentials
   ↓
5. Click "Save & Test"
   ↓
6. Connection verified
   ↓
7. MCP appears in list with ✓ Active status
```

### Using the Chat
```
1. Select MCP from dropdown
   ↓
2. Type question/command
   ↓
3. Press Enter or click Send
   ↓
4. Response appears in chat
   ↓
5. Continue conversation
```

## 🎭 Interaction States

### MCP Card States
```
┌─────────────────────┐
│ 🔷 ArgoCD           │
│ Description         │
│ ● Active            │  ← Default state
│ [Edit][Test][Del]   │
└─────────────────────┘

┌─────────────────────┐
│ 🔷 ArgoCD           │
│ Description         │
│ ● Pending           │  ← After creation, before test
│ [Edit][Test][Del]   │
└─────────────────────┘

┌─────────────────────┐
│ 🔷 ArgoCD           │
│ Connection failed   │
│ ● Error             │  ← After failed test
│ [Edit][Test][Del]   │
└─────────────────────┘
```

### Chat States
```
Empty State:
┌─────────────────────────┐
│   No messages yet...    │
│   Select an MCP and     │
│   start chatting!       │
└─────────────────────────┘

Active Chat:
┌─────────────────────────┐
│ [Multiple messages]     │
│ [Auto-scrolls to end]   │
└─────────────────────────┘

No MCP Selected:
⚠️ Please select an MCP server first
```

## 📱 Responsive Behavior

### Desktop (1280x800)
- Left panel: 350px fixed width
- Right panel: Flexible, expands to fill
- Chat messages: Max width 500px
- Comfortable spacing

### Smaller Screens
- Maintains split-view
- Chat messages wrap properly
- Scrollable areas work smoothly

## 🎯 Visual Hierarchy

### Primary Actions (Most Important)
1. **Send Button** (►) - Bright blue, prominent
2. **Add MCP** (+) - Icon button, top-right
3. **Save & Test** - Elevated button in dialogs

### Secondary Actions
- **Edit/Test/Delete** - Text buttons on cards
- **MCP Selector** - Dropdown at top of chat

### Tertiary Elements
- **Status indicators** - Small colored dots
- **Timestamps** - Small grey text
- **Descriptions** - Muted color

## 🌈 Branding

- **Primary Color**: Blue (#2196F3) - Actions, user messages
- **Success Color**: Green (#4CAF50) - Assistant, active status
- **Warning Color**: Orange (#FF9800) - Pending status
- **Error Color**: Red (#F44336) - Errors, delete actions
- **Neutral**: Grey (#9E9E9E) - Disabled, secondary text

## ✨ Animations (Flet Built-in)
- Smooth page transitions
- Button hover effects
- Dialog fade in/out
- Chat auto-scroll
- Dropdown expand/collapse

---

This visual guide shows the polished, professional UI you now have for managing and interacting with MCP servers! 🎨

