/**
 * prompt makeuper Chrome Extension - Background Service Worker
 * Handles context menu creation and actions
 */

// API Configuration - Read from manifest.json, fallback to localhost
const manifest = chrome.runtime.getManifest();
const API_BASE_URL = manifest.api_base_url || 'http://localhost:8000';
const PENDING_AUTO_OPTIMIZE_KEY = 'pendingAutoOptimize';

function getPendingStorageArea() {
  return chrome.storage.session || chrome.storage.local;
}

async function storePendingAutoOptimize(prompt, tab) {
  const storageArea = getPendingStorageArea();
  const payload = {
    prompt,
    requestId: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    requestedAt: Date.now(),
    sourceTabId: tab?.id,
    sourceWindowId: tab?.windowId
  };

  await storageArea.set({
    [PENDING_AUTO_OPTIMIZE_KEY]: payload
  });
}

/**
 * Create context menu items on extension install
 */
chrome.runtime.onInstalled.addListener(() => {
  // Enable side panel to open on extension icon click
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });

  // Main context menu item
  chrome.contextMenus.create({
    id: 'promptMakeuperRoot',
    title: '✨ Prompt Makeuper',
    contexts: ['selection']
  });

  // Optimize selected text
  chrome.contextMenus.create({
    id: 'optimizeSelection',
    parentId: 'promptMakeuperRoot',
    title: 'Optimize this selection',
    contexts: ['selection']
  });

  // Separator
  chrome.contextMenus.create({
    id: 'separator1',
    parentId: 'promptMakeuperRoot',
    type: 'separator',
    contexts: ['selection']
  });

  // Open side panel
  chrome.contextMenus.create({
    id: 'openSidePanel',
    parentId: 'promptMakeuperRoot',
    title: '📋 Open Side Panel',
    contexts: ['selection', 'page']
  });

  console.log('prompt makeuper context menus created');
});

/**
 * Handle context menu clicks
 */
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'optimizeSelection') {
    await handleOptimizeSelection(info, tab);
  } else if (info.menuItemId === 'openSidePanel') {
    await handleOpenSidePanel(tab);
  }
});

/**
 * Optimize the selected text
 */
async function handleOptimizeSelection(info, tab) {
  const selectedText = info.selectionText?.trim();

  if (!selectedText) {
    return;
  }

  try {
    if (!tab?.windowId) {
      throw new Error('No active window is available for the side panel.');
    }

    await storePendingAutoOptimize(selectedText, tab);
    await chrome.sidePanel.open({ windowId: tab.windowId });
  } catch (error) {
    console.error('Failed to auto-optimize selected text:', error);
  }
}

/**
 * Open the side panel
 */
async function handleOpenSidePanel(tab) {
  try {
    await chrome.sidePanel.open({ windowId: tab.windowId });
  } catch (error) {
    console.error('Failed to open side panel:', error);
  }
}
