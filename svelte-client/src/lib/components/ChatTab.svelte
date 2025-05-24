<script lang="ts">
	import { marked } from 'marked';

	interface Message {
		type: 'user' | 'bot';
		content: string;
	}

	export let messages: Message[];
	export let chatInput: string;
	export let onSendMessage: () => void;
	export let isLoading: boolean;
	export let errorMessage: string;
	let chatContainer: HTMLElement;
	let showScrollButton = false;

	// Check if user has scrolled up from bottom
	function checkScrollPosition() {
		if (chatContainer) {
			const { scrollTop, scrollHeight, clientHeight } = chatContainer;
			const isAtBottom = scrollTop + clientHeight >= scrollHeight - 20;
			showScrollButton = !isAtBottom && messages.length > 0;
		}
	}

	// Only auto-scroll for the very first message
	$: if (messages && chatContainer && messages.length === 1) {
		setTimeout(() => {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}, 10);
	}

	function handleScroll() {
		checkScrollPosition();
	}

	function scrollToBottom() {
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
			showScrollButton = false;
		}
	}

	function handleKeypress(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			onSendMessage();
		}
	}
</script>

<div class="space-y-4">
	<h2 class="text-xl font-semibold text-gray-800">Chat with AI Model</h2>
	<!-- Chat Window -->
	<div class="border border-gray-200 rounded-lg bg-white relative">
		<!-- Messages Area -->
		<div
			bind:this={chatContainer}
			on:scroll={handleScroll}
			class="h-96 overflow-y-auto p-4 space-y-3"
		>
			{#each messages as message}
				<div class="flex {message.type === 'user' ? 'justify-end' : 'justify-start'}">
					<div
						class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg {message.type === 'user'
							? 'bg-blue-600 text-white'
							: 'bg-gray-100 text-gray-800'}"
					>
						{#if message.type === 'bot'}
							{@html marked.parse(message.content)}
						{:else}
							{message.content}
						{/if}
					</div>
				</div>
			{/each}

			{#if isLoading}
				<div class="flex justify-start">
					<div class="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
						<div class="flex items-center space-x-2">
							<div class="animate-pulse">AI is thinking...</div>
						</div>
					</div>
				</div>
			{/if}
		</div>

		<!-- Scroll to Bottom Button -->
		{#if showScrollButton}
			<button
				on:click={scrollToBottom}
				class="absolute bottom-20 right-4 bg-blue-600 text-white p-2 rounded-full shadow-lg hover:bg-blue-700 transition-colors z-10"
				title="Scroll to bottom"
			>
				<svg
					class="w-4 h-4"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M19 14l-7 7m0 0l-7-7m7 7V3"
					/>
				</svg>
			</button>
		{/if}

		<!-- Input Area -->
		<div class="border-t border-gray-200 p-4">
			<div class="flex gap-3">
				<input
					type="text"
					bind:value={chatInput}
					on:keypress={handleKeypress}
					placeholder="Type your message..."
					disabled={isLoading}
					class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
				/>
				<button
					on:click={onSendMessage}
					disabled={isLoading || !chatInput.trim()}
					class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
				>
					Send
				</button>
			</div>
		</div>
	</div>

	<!-- Chat Error Message -->
	{#if errorMessage}
		<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
			{errorMessage}
		</div>
	{/if}
</div>
