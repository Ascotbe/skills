# TW-Blocks Component Patterns

Detailed implementation patterns for common UI components using TW-Blocks spacing system.

## Table of Contents

- [Dashboard Layouts](#dashboard-layouts)
- [Toolbars & Headers](#toolbars--headers)
- [Panels & Sidebars](#panels--sidebars)
- [Forms & Inputs](#forms--inputs)
- [Tables & Lists](#tables--lists)
- [Status Indicators](#status-indicators)
- [Chat & Messages](#chat--messages)
- [Charts & Data Viz](#charts--data-viz)
- [Timeline & Animation](#timeline--animation)
- [Code Editor Interface](#code-editor-interface)

---

## Dashboard Layouts

### Dashboard Sidebar (240px standard width)
```html
<aside class="w-[240px] bg-slate-800 text-white flex flex-col">
  <!-- Sidebar Header -->
  <div class="p-tab-4 border-b border-slate-700">
    <div class="flex items-center gap-tab-3">
      <div class="w-block-1 h-block-1 bg-blue-500 rounded-lg flex items-center justify-center">
        <svg class="w-tab-5 h-tab-5" />
      </div>
      <span class="font-semibold text-lg">AppName</span>
    </div>
  </div>
  
  <!-- Navigation -->
  <nav class="flex-1 p-tab-3">
    <ul class="space-y-tab-1">
      <li>
        <a href="#" class="flex items-center gap-tab-3 h-block-1 px-tab-3 rounded-lg bg-blue-600 text-white">
          <svg class="w-tab-4 h-tab-4" />
          <span class="text-sm">Dashboard</span>
        </a>
      </li>
      <li>
        <a href="#" class="flex items-center gap-tab-3 h-block-1 px-tab-3 rounded-lg text-slate-300 hover:bg-slate-700">
          <svg class="w-tab-4 h-tab-4" />
          <span class="text-sm">Settings</span>
        </a>
      </li>
    </ul>
  </nav>
  
  <!-- Sidebar Footer -->
  <div class="p-tab-4 border-t border-slate-700">
    <div class="flex items-center gap-tab-3">
      <div class="w-block-1 h-block-1 rounded-full bg-blue-500 flex items-center justify-center text-sm font-medium">
        AU
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-medium truncate">Admin User</p>
        <p class="text-xs text-slate-400 truncate">admin@example.com</p>
      </div>
    </div>
  </div>
</aside>
```

### Stat Card
```html
<div class="bg-white rounded-xl shadow-sm border border-gray-100 p-tab-4">
  <div class="flex items-center justify-between gap-tab-3">
    <div>
      <p class="text-sm font-medium text-gray-500">Total Revenue</p>
      <p class="mt-tab-1 text-2xl font-bold text-gray-900">$45,231.89</p>
      <p class="mt-tab-1 text-sm text-green-600 flex items-center gap-tab-1">
        <svg class="w-tab-4 h-tab-4" />
        +20.1% from last month
      </p>
    </div>
    <div class="w-block-1.5 h-block-1.5 bg-green-100 rounded-xl flex items-center justify-center">
      <svg class="w-tab-6 h-tab-6 text-green-600" />
    </div>
  </div>
</div>
```

---

## Toolbars & Headers

### Dashboard Header (64px / 2 blocks)
```html
<header class="h-block-2 bg-white border-b border-gray-200 flex items-center px-tab-4">
  <!-- Search -->
  <div class="flex-1 max-w-xl">
    <div class="relative">
      <svg class="absolute left-tab-3 top-1/2 -translate-y-1/2 w-tab-4 h-tab-4 text-gray-400" />
      <input 
        type="text" 
        placeholder="Search..." 
        class="w-full h-block-1 pl-tab-10 pr-tab-3 bg-gray-100 rounded-lg text-sm"
      />
    </div>
  </div>
  
  <!-- Actions -->
  <div class="flex items-center gap-tab-3 ml-auto">
    <button class="relative p-tab-2 rounded-lg hover:bg-gray-100">
      <svg class="w-tab-5 h-tab-5 text-gray-600" />
      <span class="absolute top-tab-1 right-tab-1 w-tab-2 h-tab-2 bg-red-500 rounded-full"></span>
    </button>
    <div class="w-block-1 h-block-1 rounded-full bg-blue-500 flex items-center justify-center text-white text-xs font-medium">
      AU
    </div>
  </div>
</header>
```

### Design Tool Toolbar (48px / 1.5 blocks)
```html
<header class="h-block-1.5 bg-neutral-900 border-b border-neutral-700 flex items-center px-tab-3">
  <!-- Logo -->
  <div class="flex items-center gap-tab-2">
    <div class="w-block-1 h-block-1 bg-blue-500 rounded flex items-center justify-center">
      <svg class="w-tab-4 h-tab-4 text-white" />
    </div>
    <span class="text-sm font-semibold">Design Tool</span>
  </div>
  
  <!-- Menu -->
  <nav class="flex items-center gap-tab-1 ml-tab-4">
    <button class="px-tab-3 py-tab-1.5 text-xs text-gray-400 hover:text-white hover:bg-neutral-800 rounded">
      File
    </button>
    <button class="px-tab-3 py-tab-1.5 text-xs text-gray-400 hover:text-white hover:bg-neutral-800 rounded">
      Edit
    </button>
  </nav>
  
  <!-- Right Actions -->
  <div class="flex items-center gap-tab-2 ml-auto">
    <button class="px-tab-3 py-tab-1.5 text-xs bg-blue-500 text-white rounded">
      Share
    </button>
    <div class="w-block-1 h-block-1 rounded-full bg-purple-500 flex items-center justify-center text-xs font-medium">
      U
    </div>
  </div>
</header>
```

### Timeline Control Bar
```html
<div class="h-[32px] border-b border-gray-800 flex items-center px-tab-2 gap-tab-2">
  <div class="flex items-center gap-0.5 bg-neutral-800 rounded-md p-0.5">
    <button class="p-tab-1 text-gray-500 hover:text-gray-300 rounded">
      <svg class="w-tab-4 h-tab-4" /> <!-- pause -->
    </button>
    <button class="p-tab-1 bg-blue-500 text-white rounded">
      <svg class="w-tab-4 h-tab-4" /> <!-- play -->
    </button>
  </div>
  
  <div class="flex items-center gap-tab-1.5 text-xs">
    <span class="text-gray-500">Frame:</span>
    <input 
      type="number" 
      value="24"
      class="w-[48px] h-tab-6 bg-neutral-800 border border-neutral-700 rounded-md px-tab-1.5 text-center text-gray-300 text-xs font-mono"
    />
  </div>
</div>
```

### Status Bar (24px / 6 tabs)
```html
<div class="h-tab-6 bg-neutral-900 border-t border-neutral-700 flex items-center justify-between px-tab-3">
  <div class="flex items-center gap-tab-4 text-xs text-gray-400">
    <span>X: 120</span>
    <span>Y: 48</span>
    <span>W: 552</span>
    <span>H: 48</span>
  </div>
  <span class="text-xs text-gray-400">Zoom: 100%</span>
</div>
```

### Zoom Controls
```html
<div class="flex items-center gap-tab-1 bg-neutral-900 rounded-lg p-tab-1.5 border border-neutral-700">
  <button class="p-tab-1 rounded hover:bg-neutral-800">
    <svg class="w-tab-4 h-tab-4" /> <!-- minus -->
  </button>
  <span class="text-xs text-gray-300 w-tab-10 text-center">100%</span>
  <button class="p-tab-1 rounded hover:bg-neutral-800">
    <svg class="w-tab-4 h-tab-4" /> <!-- plus -->
  </button>
</div>
```

---

## Panels & Sidebars

### Vertical Tool Palette (48px width)
```html
<div class="w-block-1.5 bg-neutral-900 border-r border-neutral-700 flex flex-col items-center py-tab-2 gap-tab-1">
  <button class="w-[36px] h-[36px] flex items-center justify-center rounded-md bg-blue-500/20 text-blue-400">
    <svg class="w-tab-5 h-tab-5" />
  </button>
  <button class="w-[36px] h-[36px] flex items-center justify-center rounded-md text-gray-400 hover:text-white hover:bg-neutral-800">
    <svg class="w-tab-5 h-tab-5" />
  </button>
  
  <div class="my-tab-2 w-tab-6 border-t border-neutral-700" />
  
  <button class="w-[36px] h-[36px] flex items-center justify-center rounded-md text-gray-400 hover:text-white hover:bg-neutral-800">
    <svg class="w-tab-5 h-tab-5" />
  </button>
</div>
```

### Panel with Sections (280px width)
```html
<div class="w-[280px] bg-neutral-900 border-l border-neutral-700 flex flex-col">
  <!-- Panel Tabs -->
  <div class="h-block-1 flex border-b border-neutral-700">
    <button class="flex-1 text-xs font-medium text-blue-400 border-b-2 border-blue-400">
      Design
    </button>
    <button class="flex-1 text-xs font-medium text-gray-400 hover:text-white">
      Prototype
    </button>
  </div>
  
  <!-- Section -->
  <div class="p-tab-2 border-b border-neutral-700">
    <div class="flex items-center justify-between mb-tab-2">
      <span class="text-xs font-medium text-gray-300">Position</span>
    </div>
    <div class="grid grid-cols-2 gap-tab-2">
      <div>
        <label class="text-xs text-gray-500 mb-tab-1 block">X</label>
        <input type="text" class="w-full h-tab-6 px-tab-2 bg-neutral-800 border border-neutral-700 rounded text-xs text-gray-300" />
      </div>
      <div>
        <label class="text-xs text-gray-500 mb-tab-1 block">Y</label>
        <input type="text" class="w-full h-tab-6 px-tab-2 bg-neutral-800 border border-neutral-700 rounded text-xs text-gray-300" />
      </div>
    </div>
  </div>
</div>
```

### Layers Panel Item (32px height)
```html
<div class="flex items-center gap-tab-2 h-block-1 px-tab-2 bg-blue-500/10 rounded text-blue-400 text-xs">
  <button class="w-tab-4 h-tab-4 flex items-center justify-center">
    <svg class="w-tab-3 h-tab-3" /> <!-- chevron -->
  </button>
  <svg class="w-tab-4 h-tab-4" /> <!-- layer icon -->
  <span class="flex-1 truncate">Layer Name</span>
  <button class="w-tab-4 h-tab-4 flex items-center justify-center opacity-50 hover:opacity-100">
    <svg class="w-tab-3 h-tab-3" /> <!-- visibility -->
  </button>
</div>
```

---

## Forms & Inputs

### Standard Button
```html
<button class="h-block-1 px-tab-4 rounded-tab-2 bg-blue-500 text-white">
  Click me
</button>
```

### Small Button
```html
<button class="h-tab-6 px-tab-3 rounded-tab-1.5 text-sm">
  Small
</button>
```

### Icon Button
```html
<button class="size-block-1 flex items-center justify-center rounded-tab-2">
  <svg class="w-tab-4 h-tab-4" />
</button>
```

### Input Field
```html
<input 
  type="text" 
  class="h-block-1 px-tab-3 rounded-tab-2 border border-gray-300"
/>
```

### Card
```html
<div class="p-tab-4 rounded-block-0.5 bg-white shadow-sm border">
  <h3 class="text-lg font-semibold">Title</h3>
  <p class="mt-tab-2 text-gray-600">Description</p>
</div>
```

---

## Tables & Lists

### Table Rows
```html
<table class="w-full">
  <thead>
    <tr class="border-b">
      <th class="pb-tab-3 text-left text-sm font-medium">Name</th>
      <th class="pb-tab-3 text-left text-sm font-medium">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr class="border-b">
      <td class="py-tab-3">Project Alpha</td>
      <td class="py-tab-3">Active</td>
    </tr>
  </tbody>
</table>
```

### Email/Message List (Dense)
```html
<div class="h-tab-8 px-tab-3 py-tab-2 hover:bg-gray-50 border-b flex items-center gap-tab-3">
  <div class="w-block-1 h-block-1 rounded-full bg-blue-500 flex-shrink-0"></div>
  <div class="flex-1 min-w-0">
    <div class="flex items-baseline gap-tab-2">
      <span class="font-semibold text-sm truncate">Sender Name</span>
      <span class="text-xs text-gray-500">2:30 PM</span>
    </div>
    <p class="text-sm truncate">Email subject line...</p>
  </div>
</div>
```

**Dense List Heights:**
- List items: `h-tab-8` (32px) or `h-tab-10` (40px)
- Compact: `py-tab-2` padding
- Icons/avatars: `size-block-1` (32px)

---

## Status Indicators

### Status Badges
```html
<span class="px-tab-2 py-tab-0.5 text-xs rounded-tab-1 bg-green-100 text-green-700">
  Active
</span>
<span class="px-tab-2 py-tab-0.5 text-xs rounded-tab-1 bg-gray-100 text-gray-700">
  Pending
</span>
```

### Progress Bars
```html
<div class="flex items-center gap-tab-2">
  <div class="w-tab-20 h-tab-2 bg-gray-200 rounded-full overflow-hidden">
    <div class="h-full w-3/4 bg-blue-500"></div>
  </div>
  <span class="text-xs text-gray-500">75%</span>
</div>
```

### Active & Selected States

#### Selected Items (Navigation, Tools, Layers)
```html
<!-- Active nav item -->
<button class="h-block-1 px-tab-3 bg-blue-600 text-white rounded">
  Active
</button>

<!-- Selected layer -->
<div class="h-tab-6 px-tab-2 bg-purple-500/20 border border-purple-500/40 rounded">
  Layer 1
</div>

<!-- Active tool -->
<button class="size-block-1 bg-orange-500/20 border border-orange-500 rounded">
  🔧
</button>
```

#### Hover States
Use subtle background changes:
- Default panels: `hover:bg-gray-800`
- Selected context: `hover:bg-blue-700`
- Tools: `hover:bg-gray-700`

---

## Chat & Messages

### Chat Message Bubbles
```html
<!-- User message -->
<div class="flex gap-tab-3 justify-end">
  <div class="max-w-[70%] px-tab-4 py-tab-3 bg-blue-500 text-white rounded-tab-4 rounded-br-tab-1">
    <p class="text-sm">User message here</p>
  </div>
  <div class="size-block-1 rounded-full bg-blue-600 flex-shrink-0"></div>
</div>

<!-- AI/System message -->
<div class="flex gap-tab-3">
  <div class="size-block-1 rounded-full bg-gray-300 flex-shrink-0"></div>
  <div class="max-w-[70%] px-tab-4 py-tab-3 bg-gray-100 rounded-tab-4 rounded-bl-tab-1">
    <p class="text-sm">AI response here</p>
  </div>
</div>

<!-- Message spacing -->
<div class="space-y-tab-6">
  <!-- Messages here -->
</div>
```

**Comfortable message spacing:** `space-y-tab-6` (24px)

---

## Charts & Data Viz

### Chart Container
```html
<!-- Chart with header -->
<div class="bg-white rounded-tab-3 p-tab-6">
  <h3 class="text-lg font-semibold mb-tab-4">Revenue Trend</h3>
  <div class="h-block-8 bg-gray-50 rounded flex items-center justify-center">
    <!-- Chart renders here -->
    <span class="text-gray-400">Chart Area (256px height)</span>
  </div>
</div>
```

**Recommended chart heights:**
- Small: `h-block-6` (192px)
- Medium: `h-block-8` (256px)
- Large: `h-block-12` (384px)

---

## Timeline & Animation

### Timeline / Animation Panel
```html
<!-- Bottom timeline panel -->
<div class="h-[120px] bg-gray-900 border-t border-gray-800 flex flex-col">
  <!-- Playback controls -->
  <div class="h-block-1 px-tab-4 flex items-center gap-tab-3 border-b border-gray-800">
    <button class="size-block-1 hover:bg-gray-800 rounded">▶</button>
    <button class="size-block-1 hover:bg-gray-800 rounded">⏸</button>
    <span class="text-xs text-gray-400">Frame: 1 / 120</span>
  </div>
  
  <!-- Timeline tracks -->
  <div class="flex-1 overflow-y-auto p-tab-2">
    <div class="space-y-tab-1">
      <div class="h-tab-6 bg-gray-800 rounded px-tab-2 flex items-center text-xs">
        Transform
      </div>
      <div class="h-tab-6 bg-gray-800 rounded px-tab-2 flex items-center text-xs">
        Material
      </div>
    </div>
  </div>
</div>
```

---

## Code Editor Interface

### Full IDE Layout
```html
<!-- Full IDE layout with 3 panels -->
<div class="flex h-screen">
  <!-- File tree sidebar -->
  <aside class="w-[200px] bg-gray-900 border-r border-gray-800">
    <div class="p-tab-2">
      <div class="h-tab-5 px-tab-2 text-xs hover:bg-gray-800 rounded">
        📁 src/
      </div>
    </div>
  </aside>
  
  <!-- Code editor -->
  <main class="flex-1 flex flex-col">
    <!-- Toolbar -->
    <div class="h-block-1 bg-gray-900 border-b border-gray-800 px-tab-3 flex items-center gap-tab-2">
      <div class="px-tab-3 py-tab-1 text-xs bg-gray-800 rounded">file.tsx</div>
    </div>
    
    <!-- Code area -->
    <div class="flex-1 bg-gray-950 p-tab-4 overflow-auto font-mono text-sm">
      <!-- Code here -->
    </div>
    
    <!-- Status bar -->
    <div class="h-tab-5 bg-gray-900 border-t border-gray-800 px-tab-3 flex items-center text-xs">
      Line 1, Col 1
    </div>
  </main>
  
  <!-- Properties panel -->
  <aside class="w-[220px] bg-gray-900 border-l border-gray-800 p-tab-3">
    <input class="h-tab-6 w-full px-tab-2 bg-gray-800 text-xs rounded" />
  </aside>
</div>
```

### IDE Panel Widths
- File tree: `w-[200px]` or `w-[240px]`
- Properties panel: `w-[220px]` or `w-[280px]`
- Sidebar: `w-block-8` (256px) or `w-block-10` (320px)
