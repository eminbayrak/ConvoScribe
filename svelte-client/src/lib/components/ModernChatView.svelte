<script lang="ts">
	import { marked } from '../markdown.js';
	import { onDestroy } from 'svelte';

	interface Message {
		id: string;
		type: 'user' | 'bot';
		content: string;
		timestamp: Date;
		images?: string[]; // Base64 encoded images
		isTyping?: boolean; // For typewriter effect
	}

	export let messages: Message[] = [];
	export let onSendMessage: (message: string, images?: string[]) => void;
	export let isLoading: boolean = false;

	let messageInput = '';
	let chatContainer: HTMLElement;
	let isUserScrolling = false;
	let scrollTimeout: ReturnType<typeof setTimeout>;
	let lastMessageCount = 0;
	let fileInput: HTMLInputElement;
	let uploadedImages: string[] = [];
	let isDragOver = false;

	// Typewriter effect variables
	let typingMessageId: string | null = null;
	let currentTypingContent: string = '';

	// Track the currently typing message
	$: typingMessage = messages.find((m) => m.isTyping);
	$: if (typingMessage) {
		typingMessageId = typingMessage.id;
		currentTypingContent = typingMessage.content;
	} else {
		typingMessageId = null;
		currentTypingContent = '';
	}

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

	// Auto-scroll during typewriter effect
	$: if (currentTypingContent && chatContainer && !isUserScrolling) {
		setTimeout(() => {
			if (chatContainer && !isUserScrolling) {
				const { scrollTop, scrollHeight, clientHeight } = chatContainer;
				const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;

				// Scroll to bottom during typing if user is near bottom
				if (isNearBottom) {
					chatContainer.scrollTop = chatContainer.scrollHeight;
				}
			}
		}, 10);
	}
	function handleSend() {
		if ((messageInput.trim() || uploadedImages.length > 0) && !isLoading) {
			onSendMessage(messageInput.trim(), uploadedImages.length > 0 ? uploadedImages : undefined);
			messageInput = '';
			uploadedImages = [];
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

	// Image handling functions
	function handleFileSelect(event: Event) {
		const target = event.target as HTMLInputElement;
		if (target.files) {
			Array.from(target.files).forEach((file) => {
				if (file.type.startsWith('image/')) {
					const reader = new FileReader();
					reader.onload = (e) => {
						if (e.target?.result) {
							uploadedImages = [...uploadedImages, e.target.result as string];
						}
					};
					reader.readAsDataURL(file);
				}
			});
		}
		// Reset the input
		target.value = '';
	}

	function handlePaste(event: ClipboardEvent) {
		const items = event.clipboardData?.items;
		if (items) {
			Array.from(items).forEach((item) => {
				if (item.type.startsWith('image/')) {
					const file = item.getAsFile();
					if (file) {
						const reader = new FileReader();
						reader.onload = (e) => {
							if (e.target?.result) {
								uploadedImages = [...uploadedImages, e.target.result as string];
							}
						};
						reader.readAsDataURL(file);
					}
				}
			});
		}
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
		isDragOver = true;
	}

	function handleDragLeave(event: DragEvent) {
		event.preventDefault();
		isDragOver = false;
	}

	function handleDrop(event: DragEvent) {
		event.preventDefault();
		isDragOver = false;

		const files = event.dataTransfer?.files;
		if (files) {
			Array.from(files).forEach((file) => {
				if (file.type.startsWith('image/')) {
					const reader = new FileReader();
					reader.onload = (e) => {
						if (e.target?.result) {
							uploadedImages = [...uploadedImages, e.target.result as string];
						}
					};
					reader.readAsDataURL(file);
				}
			});
		}
	}

	function removeImage(index: number) {
		uploadedImages = uploadedImages.filter((_, i) => i !== index);
	}

	function openFileDialog() {
		fileInput.click();
	}

	// Cleanup timeout on component destroy
	onDestroy(() => {
		if (scrollTimeout) {
			clearTimeout(scrollTimeout);
		}
	});
</script>

<div class="flex flex-col h-full bg-theme-primary">
	<!-- Messages Container -->
	<div bind:this={chatContainer} on:scroll={handleScroll} class="flex-1 overflow-y-auto">
		{#if messages.length === 0}
			<!-- Welcome Screen -->
			<div
				class="flex flex-col items-center justify-center h-full p-8 text-center max-w-2xl mx-auto"
			>
				<div class="w-12 h-12 bg-btn-primary rounded-full flex items-center justify-center mb-6">
					<svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
						/>
					</svg>
				</div>
				<h2 class="text-xl font-medium text-theme-primary mb-2">How can I help you today?</h2>
				<p class="text-theme-muted mb-8">
					I can help with questions, analyze video content, or have conversations about any topic.
				</p>
			</div>
		{:else}
			<!-- Messages -->
			<div class="max-w-3xl mx-auto py-8">
				{#each messages as message}
					<div class="group relative px-6 py-6 mb-4">
						<div class="flex gap-4">
							<!-- Avatar -->
							<div class="flex-shrink-0 mt-1">
								{#if message.type === 'user'}
									<div class="w-7 h-7 bg-chat-user rounded-sm flex items-center justify-center">
										<svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
											<path
												fill-rule="evenodd"
												d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z"
												clip-rule="evenodd"
											/>
										</svg>
									</div>
								{:else}
									<div class="w-7 h-7 bg-chat-bot rounded-sm flex items-center justify-center">
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
								<!-- Display images if present -->
								{#if message.images && message.images.length > 0}
									<div class="mb-4 flex flex-wrap gap-3">
										{#each message.images as image}
											<div class="relative group">
												<img
													src={image}
													alt="Uploaded image"
													class="max-w-sm max-h-64 rounded-lg border border-theme-primary object-cover cursor-pointer hover:opacity-90 transition-opacity"
													on:click={() => window.open(image, '_blank')}
												/>
											</div>
										{/each}
									</div>
								{/if}
								<div class="prose prose-lg max-w-none text-theme-primary leading-relaxed">
									{#if message.type === 'bot'}
										{#if message.isTyping && message.id === typingMessageId}
											{@html marked.parse(currentTypingContent)}
											<span class="animate-pulse">▋</span>
										{:else}
											{@html marked.parse(message.content)}
										{/if}
									{:else if message.content}
										<p class="text-theme-primary text-lg leading-relaxed">{message.content}</p>
									{/if}
								</div>
							</div>
						</div>
					</div>
				{/each}
				<!-- Loading indicator (only show when not streaming/typing) -->
				{#if isLoading && !typingMessageId}
					<div class="group relative px-6 py-6 mb-4">
						<div class="flex gap-4">
							<div class="flex-shrink-0 mt-1">
								<div class="w-7 h-7 bg-chat-bot rounded-sm flex items-center justify-center">
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
											d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2 2v10a2 2 0 002 2z"
										/>
									</svg>
								</div>
							</div>
							<div class="flex-1 min-w-0">
								<div class="flex items-center gap-2">
									<div class="flex gap-1">
										<div class="w-2 h-2 bg-theme-muted rounded-full animate-bounce"></div>
										<div
											class="w-2 h-2 bg-theme-muted rounded-full animate-bounce"
											style="animation-delay: 0.1s"
										></div>
										<div
											class="w-2 h-2 bg-theme-muted rounded-full animate-bounce"
											style="animation-delay: 0.2s"
										></div>
									</div>
								</div>
							</div>
						</div>
					</div>
				{/if}
			</div>
		{/if}
	</div>
	<!-- Input Area -->
	<div class="p-4 bg-theme-primary">
		<div class="max-w-3xl mx-auto">
			<!-- Image Preview Area -->
			{#if uploadedImages.length > 0}
				<div class="mb-3 p-3 bg-theme-secondary rounded-xl border border-theme-primary">
					<div class="flex items-center justify-between mb-2">
						<span class="text-sm font-medium text-theme-primary">Attached Images</span>
						<button
							on:click={() => (uploadedImages = [])}
							class="text-xs text-theme-secondary hover:text-theme-primary transition-colors"
						>
							Clear all
						</button>
					</div>
					<div class="flex flex-wrap gap-2">
						{#each uploadedImages as image, index}
							<div class="relative group">
								<img
									src={image}
									alt="Preview"
									class="w-20 h-20 object-cover rounded-lg border border-theme-primary"
								/>
								<button
									on:click={() => removeImage(index)}
									class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full text-xs hover:bg-red-600 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
									aria-label="Remove image"
								>
									×
								</button>
							</div>
						{/each}
					</div>
				</div>
			{/if}

			<!-- Input Container -->
			<div
				class="relative {isDragOver ? 'ring-2 ring-blue-400 rounded-3xl' : ''}"
				on:dragover={handleDragOver}
				on:dragleave={handleDragLeave}
				on:drop={handleDrop}
			>
				<div
					class="relative bg-theme-secondary rounded-3xl shadow-sm focus-within:shadow-md transition-all duration-200"
				>
					<textarea
						bind:value={messageInput}
						on:keypress={handleKeypress}
						on:paste={handlePaste}
						placeholder="Message ConvoScribe..."
						disabled={isLoading}
						rows="1"
						class="w-full resize-none pl-4 pr-16 py-4 bg-transparent text-theme-primary placeholder-theme-muted border-0 focus:ring-0 focus:outline-none disabled:opacity-50 rounded-3xl"
						style="min-height: 56px; max-height: 200px; line-height: 1.5;"
					></textarea>

					<div class="absolute right-2 bottom-2 flex items-center gap-1">
						<!-- Image Upload Button -->
						<button
							on:click={openFileDialog}
							disabled={isLoading}
							aria-label="Upload image"
							class="p-2 text-theme-muted hover:text-theme-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors rounded-xl hover:bg-theme-tertiary"
						>
							<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="1.5"
									d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
								/>
							</svg>
						</button>

						<!-- Send Button -->
						<button
							on:click={handleSend}
							disabled={isLoading || (!messageInput.trim() && uploadedImages.length === 0)}
							aria-label="Send message"
							class="w-8 h-8 {messageInput.trim() || uploadedImages.length > 0
								? 'bg-btn-primary hover:bg-btn-primary'
								: 'bg-theme-tertiary text-theme-muted'} rounded-xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center"
						>
							<svg
								class="w-4 h-4"
								fill="none"
								stroke="currentColor"
								viewBox="0 0 24 24"
								stroke-width="2"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
								/>
							</svg>
						</button>
					</div>
				</div>
			</div>

			<!-- Hidden File Input -->
			<input
				bind:this={fileInput}
				type="file"
				accept="image/*"
				multiple
				on:change={handleFileSelect}
				class="hidden"
			/>

			<!-- Drag Overlay -->
			{#if isDragOver}
				<div
					class="absolute inset-0 bg-status-info bg-opacity-10 border-2 border-dashed border-status-info rounded-3xl flex items-center justify-center z-10"
				>
					<div class="text-status-info text-center">
						<svg class="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
							/>
						</svg>
						<p class="font-medium">Drop images here</p>
					</div>
				</div>
			{/if}
		</div>
	</div>
</div>
