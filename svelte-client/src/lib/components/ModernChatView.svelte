<script lang="ts">
	import { marked } from 'marked';
	import { onDestroy } from 'svelte';

	interface Message {
		type: 'user' | 'bot';
		content: string;
		timestamp: Date;
	}

	export let messages: Message[] = [];
	export let onSendMessage: (message: string) => void;
	export let isLoading: boolean = false;
	let messageInput = '';
	let chatContainer: HTMLElement;
	let isUserScrolling = false;
	let scrollTimeout: number;
	let lastMessageCount = 0;

	// Track if user is manually scrolling
	function handleScroll() {
		if (chatContainer) {
			isUserScrolling = true;

			// Clear any existing timeout
			if (scrollTimeout) {
				clearTimeout(scrollTimeout);
			}

			// Reset scrolling flag after user stops scrolling
			scrollTimeout = setTimeout(() => {
				isUserScrolling = false;
			}, 150);
		}
	}

	// Only auto-scroll when messages are added and user isn't manually scrolling
	$: if (messages && chatContainer && messages.length > lastMessageCount) {
		lastMessageCount = messages.length;

		// Only auto-scroll if user isn't currently scrolling
		if (!isUserScrolling) {
			setTimeout(() => {
				if (chatContainer && !isUserScrolling) {
					const { scrollTop, scrollHeight, clientHeight } = chatContainer;
					const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;

					// Only scroll if user is near bottom or it's the first message
					if (isNearBottom || messages.length === 1) {
						chatContainer.scrollTop = chatContainer.scrollHeight;
					}
				}
			}, 50);
		}
	}
	function handleSend() {
		if (messageInput.trim() && !isLoading) {
			onSendMessage(messageInput.trim());
			messageInput = '';
			// Reset scrolling state and force scroll to bottom when user sends a message
			isUserScrolling = false;
		}
	}
	function handleKeypress(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSend();
		}
	}

	// Cleanup timeout on component destroy
	onDestroy(() => {
		if (scrollTimeout) {
			clearTimeout(scrollTimeout);
		}
	});
</script>

<div class="flex flex-col h-full bg-white">
	<!-- Header -->
	<div class="flex items-center justify-between p-4 border-b border-gray-200">
		<div>
			<h1 class="text-xl font-semibold text-gray-900">Chat with AI</h1>
			<p class="text-sm text-gray-500">Ask me anything or discuss video content</p>
		</div>
		<div class="flex items-center gap-2">
			<div class="w-2 h-2 bg-green-500 rounded-full"></div>
			<span class="text-xs text-gray-500">Online</span>
		</div>
	</div>
	<!-- Messages Container -->
	<div bind:this={chatContainer} on:scroll={handleScroll} class="flex-1 overflow-y-auto">
		{#if messages.length === 0}
			<!-- Welcome Screen -->
			<div class="flex flex-col items-center justify-center h-full p-8 text-center">
				<div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
					<svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
						/>
					</svg>
				</div>
				<h2 class="text-2xl font-semibold text-gray-900 mb-2">Start a conversation</h2>
				<p class="text-gray-600 max-w-md">
					I'm here to help you with questions, discuss video content, or just have a conversation.
					What would you like to talk about?
				</p>
				<div class="grid grid-cols-1 md:grid-cols-2 gap-3 mt-8 max-w-2xl">
					<button
						on:click={() => (messageInput = 'What can you help me with?')}
						class="p-4 text-left border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
					>
						<div class="font-medium text-gray-900">What can you help me with?</div>
						<div class="text-sm text-gray-500">Learn about my capabilities</div>
					</button>
					<button
						on:click={() => (messageInput = 'Explain a complex topic to me')}
						class="p-4 text-left border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
					>
						<div class="font-medium text-gray-900">Explain a complex topic</div>
						<div class="text-sm text-gray-500">Get detailed explanations</div>
					</button>
					<button
						on:click={() => (messageInput = 'Help me understand a YouTube video')}
						class="p-4 text-left border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
					>
						<div class="font-medium text-gray-900">Analyze video content</div>
						<div class="text-sm text-gray-500">Discuss video transcripts</div>
					</button>
					<button
						on:click={() => (messageInput = 'What are some good learning strategies?')}
						class="p-4 text-left border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
					>
						<div class="font-medium text-gray-900">Learning tips</div>
						<div class="text-sm text-gray-500">Get study advice</div>
					</button>
				</div>
			</div>
		{:else}
			<!-- Messages -->
			<div class="max-w-4xl mx-auto">
				{#each messages as message}
					<div
						class="group relative px-4 py-6 {message.type === 'user' ? 'bg-white' : 'bg-gray-50'}"
					>
						<div class="flex gap-4">
							<!-- Avatar -->
							<div class="flex-shrink-0">
								{#if message.type === 'user'}
									<div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
										<svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
											<path
												fill-rule="evenodd"
												d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
												clip-rule="evenodd"
											/>
										</svg>
									</div>
								{:else}
									<div class="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
										<svg
											class="w-4 h-4 text-white"
											fill="none"
											stroke="currentColor"
											viewBox="0 0 24 24"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												stroke-width="2"
												d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
											/>
										</svg>
									</div>
								{/if}
							</div>

							<!-- Message Content -->
							<div class="flex-1 min-w-0">
								<div class="font-medium text-sm text-gray-900 mb-1">
									{message.type === 'user' ? 'You' : 'ConvoScribe '}
								</div>
								<div class="prose prose-sm max-w-none text-gray-800">
									{#if message.type === 'bot'}
										{@html marked.parse(message.content)}
									{:else}
										{message.content}
									{/if}
								</div>
								<div class="text-xs text-gray-400 mt-2">
									{new Intl.DateTimeFormat('en-US', {
										hour: '2-digit',
										minute: '2-digit'
									}).format(message.timestamp)}
								</div>
							</div>
						</div>
					</div>
				{/each}

				<!-- Loading indicator -->
				{#if isLoading}
					<div class="group relative px-4 py-6 bg-gray-50">
						<div class="flex gap-4">
							<div class="flex-shrink-0">
								<div class="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center">
									<svg
										class="w-4 h-4 text-white"
										fill="none"
										stroke="currentColor"
										viewBox="0 0 24 24"
									>
										<path
											stroke-linecap="round"
											stroke-linejoin="round"
											stroke-width="2"
											d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
										/>
									</svg>
								</div>
							</div>
							<div class="flex-1 min-w-0">
								<div class="font-medium text-sm text-gray-900 mb-1">ConvoScribe</div>
								<div class="flex items-center gap-2">
									<div class="flex gap-1">
										<div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
										<div
											class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
											style="animation-delay: 0.1s"
										></div>
										<div
											class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
											style="animation-delay: 0.2s"
										></div>
									</div>
									<span class="text-sm text-gray-500">AI is thinking...</span>
								</div>
							</div>
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>

	<!-- Input Area -->
	<div class="border-t border-gray-200 bg-white">
		<div class="max-w-4xl mx-auto p-4">
			<div class="flex gap-3 items-end">
				<div class="flex-1 relative">
					<textarea
						bind:value={messageInput}
						on:keypress={handleKeypress}
						placeholder="Send a message..."
						disabled={isLoading}
						rows="1"
						class="w-full resize-none px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 bg-white"
						style="min-height: 44px; max-height: 120px;"
					></textarea>
					<button
						on:click={handleSend}
						disabled={isLoading || !messageInput.trim()}
						class="absolute right-2 bottom-2 p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
							/>
						</svg>
					</button>
				</div>
			</div>
			<div class="text-xs text-gray-500 mt-2 text-center">
				ConvoScribe can make mistakes. Consider checking important information.
			</div>
		</div>
	</div>
</div>
