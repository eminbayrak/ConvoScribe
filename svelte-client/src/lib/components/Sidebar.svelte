<script lang="ts">
	import ThemeToggle from './ThemeToggle.svelte';

	export let activeView: 'chat' | 'summarizer' | 'explainer' = 'chat';
	export let onViewChange: (view: 'chat' | 'summarizer' | 'explainer') => void;
	export let chatSessions: Array<{ id: string; title: string; timestamp: Date }> = [];
	export let onNewChat: () => void;
	export let onSelectChat: (sessionId: string) => void;
	export let selectedChatId: string | null = null;
	function handleViewChange(view: 'chat' | 'summarizer' | 'explainer') {
		onViewChange(view);
	}

	function truncateTitle(title: string, maxLength = 30) {
		return title.length > maxLength ? title.substring(0, maxLength) + '...' : title;
	}
</script>

<div class="w-64 bg-sidebar text-sidebar h-screen flex flex-col">
	<!-- Header -->
	<div class="p-4 border-b border-sidebar">
		<h1 class="text-xl font-semibold">ConvoScribe</h1>
	</div>
	<!-- New Chat Button -->
	<div class="p-4">
		<button
			on:click={onNewChat}
			class="w-full flex items-center gap-3 px-3 py-2 rounded-lg bg-btn-secondary hover:bg-btn-secondary transition-colors border border-sidebar"
		>
			<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
			</svg>
			New Chat
		</button>
	</div>

	<!-- Navigation -->
	<div class="px-4 mb-4">
		<div class="space-y-1">
			<button
				on:click={() => handleViewChange('chat')}
				class="w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors {activeView ===
				'chat'
					? 'bg-sidebar-active text-sidebar'
					: 'text-sidebar-muted hover:bg-sidebar-hover hover:text-sidebar'}"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
					/>
				</svg>
				Chat
			</button>
			<button
				on:click={() => handleViewChange('summarizer')}
				class="w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors {activeView ===
				'summarizer'
					? 'bg-sidebar-active text-sidebar'
					: 'text-sidebar-muted hover:bg-sidebar-hover hover:text-sidebar'}"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
					/>
				</svg>
				Summarize
			</button>
			<button
				on:click={() => handleViewChange('explainer')}
				class="w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors {activeView ===
				'explainer'
					? 'bg-sidebar-active text-sidebar'
					: 'text-sidebar-muted hover:bg-sidebar-hover hover:text-sidebar'}"
			>
				<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
					/>
				</svg>
				Explain
			</button>
		</div>
	</div>

	<!-- Chat History (only show when in chat mode) -->
	{#if activeView === 'chat'}
		<div class="flex-1 overflow-y-auto px-4 pb-4">
			<div class="text-xs text-sidebar-muted uppercase tracking-wide mb-2">Recent Chats</div>
			<div class="space-y-1">
				{#each chatSessions as session}
					<button
						on:click={() => onSelectChat(session.id)}
						class="w-full text-left px-3 py-2 rounded-lg transition-colors {selectedChatId ===
						session.id
							? 'bg-sidebar-active'
							: 'hover:bg-sidebar-hover'} group"
					>
						<div class="text-sm text-sidebar">{truncateTitle(session.title)}</div>
						<div class="text-xs text-sidebar-muted">
							{new Intl.DateTimeFormat('en-US', {
								month: 'short',
								day: 'numeric',
								hour: '2-digit',
								minute: '2-digit'
							}).format(session.timestamp)}
						</div>
					</button>
				{/each}
			</div>
		</div>
	{/if}

	<!-- Footer -->
	<div class="p-4 border-t border-sidebar space-y-3">
		<!-- Theme Toggle -->
		<ThemeToggle />

		<!-- App Info -->
		<div class="text-xs text-sidebar-muted">
			<div>ConvoScribe v1.0</div>
			<div class="mt-1">Powered by Ollama</div>
		</div>
	</div>
</div>
