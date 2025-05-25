<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';
	import ModernChatView from '$lib/components/ModernChatView.svelte';
	import VideoAnalysisView from '$lib/components/VideoAnalysisView.svelte';
	import { summarizeVideo, explainVideo, sendChatMessage } from '$lib/api';

	// App state
	let activeView: 'chat' | 'summarizer' | 'explainer' = 'chat';

	// Chat state
	let currentChatId = 'default';
	let chatSessions = [{ id: 'default', title: 'New Chat', timestamp: new Date() }];
	let chatMessages: Array<{
		id: string;
		type: 'user' | 'bot';
		content: string;
		timestamp: Date;
		images?: string[];
		isTyping?: boolean;
	}> = [];
	let isChatLoading = false;
	// Video analysis state - separate for each mode
	let summarizerState = {
		isLoading: false,
		result: '',
		error: ''
	};
	let explainerState = {
		isLoading: false,
		result: '',
		error: ''
	};
	function handleViewChange(view: 'chat' | 'summarizer' | 'explainer') {
		console.log('handleViewChange called with:', view);
		activeView = view;
		// No need to clear errors when switching views since each view has its own state
	}

	function handleNewChat() {
		console.log('handleNewChat called');
		const newChatId = `chat-${Date.now()}`;
		const newSession = {
			id: newChatId,
			title: 'New Chat',
			timestamp: new Date()
		};

		chatSessions = [newSession, ...chatSessions];
		currentChatId = newChatId;
		chatMessages = [];
		activeView = 'chat';
	}

	function handleSelectChat(sessionId: string) {
		currentChatId = sessionId;
		// In a real app, you'd load the chat history here
		// For now, we'll just switch to an empty chat
		chatMessages = [];
		activeView = 'chat';
	}

	async function handleSendMessage(message: string, images?: string[]) {
		// Add user message
		const userMessageId = `user-${Date.now()}`;
		chatMessages = [
			...chatMessages,
			{
				id: userMessageId,
				type: 'user',
				content: message,
				timestamp: new Date(),
				images: images
			}
		];

		// Update chat title with first message
		if (chatMessages.length === 1) {
			const sessionIndex = chatSessions.findIndex((s) => s.id === currentChatId);
			if (sessionIndex !== -1) {
				chatSessions[sessionIndex].title =
					message.length > 30
						? message.substring(0, 30) + '...'
						: images && images.length > 0
							? 'Image conversation'
							: 'New Chat';
			}
		}

		isChatLoading = true;

		// Create a bot message for typing effect
		const botMessageId = `bot-${Date.now()}`;
		chatMessages = [
			...chatMessages,
			{
				id: botMessageId,
				type: 'bot',
				content: '',
				timestamp: new Date(),
				isTyping: true
			}
		];

		try {
			let accumulatedContent = '';

			// Prepare conversation history for context (exclude current typing message)
			const conversationHistory = chatMessages
				.filter((msg) => !msg.isTyping && msg.content.trim()) // Exclude typing messages and empty content
				.map((msg) => ({
					type: msg.type,
					content: msg.content
				}));

			// Send message with streaming enabled and conversation history
			const result = await sendChatMessage(
				message || "I've shared an image with you.",
				images,
				(chunk: string) => {
					// Handle each chunk for typewriter effect
					accumulatedContent += chunk;

					// Update the typing message content
					chatMessages = chatMessages.map((msg) =>
						msg.id === botMessageId ? { ...msg, content: accumulatedContent } : msg
					);
				},
				conversationHistory // Pass conversation history for context
			);

			if (result.success && result.data) {
				// Finalize the message and remove typing indicator
				chatMessages = chatMessages.map((msg) =>
					msg.id === botMessageId
						? { ...msg, content: result.data?.reply || '', isTyping: false }
						: msg
				);
			} else {
				// Handle error
				chatMessages = chatMessages.map((msg) =>
					msg.id === botMessageId
						? {
								...msg,
								content: `Sorry, I encountered an error: ${result.error || 'Unknown error'}`,
								isTyping: false
							}
						: msg
				);
			}
		} catch (error) {
			// Handle unexpected errors
			chatMessages = chatMessages.map((msg) =>
				msg.id === botMessageId
					? {
							...msg,
							content: 'Sorry, I encountered an unexpected error. Please try again.',
							isTyping: false
						}
					: msg
			);
		} finally {
			isChatLoading = false;
		}
	}
	async function handleVideoAnalysis(url: string, mode: 'summarizer' | 'explainer') {
		// Get the appropriate state object
		const state = mode === 'summarizer' ? summarizerState : explainerState;

		state.isLoading = true;
		state.error = '';
		state.result = '';

		try {
			const result = mode === 'summarizer' ? await summarizeVideo(url) : await explainVideo(url);

			if (result.success && result.data) {
				state.result =
					mode === 'summarizer'
						? (result.data as { summary: string }).summary
						: (result.data as { explanation: string }).explanation;
			} else {
				state.error = result.error || 'Failed to analyze video';
			}
		} catch (error) {
			state.error = 'An unexpected error occurred while analyzing the video';
		} finally {
			state.isLoading = false;
		}

		// Trigger reactivity by reassigning the state objects
		if (mode === 'summarizer') {
			summarizerState = { ...summarizerState };
		} else {
			explainerState = { ...explainerState };
		}
	}
</script>

<div class="flex h-screen bg-white">
	<!-- Sidebar -->
	<Sidebar
		{activeView}
		onViewChange={handleViewChange}
		{chatSessions}
		onNewChat={handleNewChat}
		onSelectChat={handleSelectChat}
		selectedChatId={currentChatId}
	/>

	<!-- Main Content -->
	<div class="flex-1 h-screen overflow-hidden bg-white">
		{#if activeView === 'chat'}
			<ModernChatView
				messages={chatMessages}
				onSendMessage={handleSendMessage}
				isLoading={isChatLoading}
			/>
		{:else if activeView === 'summarizer'}
			<VideoAnalysisView
				mode="summarizer"
				onAnalyze={handleVideoAnalysis}
				isLoading={summarizerState.isLoading}
				result={summarizerState.result}
				error={summarizerState.error}
			/>
		{:else if activeView === 'explainer'}
			<VideoAnalysisView
				mode="explainer"
				onAnalyze={handleVideoAnalysis}
				isLoading={explainerState.isLoading}
				result={explainerState.result}
				error={explainerState.error}
			/>
		{/if}
	</div>
</div>
