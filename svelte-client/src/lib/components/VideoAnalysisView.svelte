<script lang="ts">
	import { marked } from 'marked';

	export let mode: 'summarizer' | 'explainer';
	export let onAnalyze: (url: string, mode: 'summarizer' | 'explainer') => Promise<void>;
	export let isLoading: boolean = false;
	export let result: string = '';
	export let error: string = '';

	let youtubeUrl = '';

	async function handleAnalyze() {
		if (youtubeUrl.trim()) {
			await onAnalyze(youtubeUrl.trim(), mode);
		}
	}

	function handleKeypress(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleAnalyze();
		}
	}

	function extractVideoId(url: string): string | null {
		const regex = /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/;
		const match = url.match(regex);
		return match ? match[1] : null;
	}

	$: videoId = extractVideoId(youtubeUrl);
	$: thumbnailUrl = videoId ? `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg` : null;
</script>

<div class="flex flex-col h-full bg-white">
	<!-- Header -->
	<div class="p-6 border-b border-gray-200">
		<div class="max-w-4xl mx-auto">
			<h1 class="text-2xl font-semibold text-gray-900 mb-2">
				{mode === 'summarizer' ? 'Video Summarizer' : 'Video Explainer'}
			</h1>
			<p class="text-gray-600">
				{mode === 'summarizer'
					? 'Get concise summaries of YouTube videos'
					: 'Get detailed explanations of YouTube video content'}
			</p>
		</div>
	</div>

	<!-- Content Area -->
	<div class="flex-1 overflow-y-auto">
		<div class="max-w-4xl mx-auto p-6">
			<!-- URL Input Section -->
			<div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
				<label for="youtube-url" class="block text-sm font-medium text-gray-700 mb-3">
					YouTube URL
				</label>
				<div class="flex gap-3">
					<input
						id="youtube-url"
						type="url"
						bind:value={youtubeUrl}
						on:keypress={handleKeypress}
						placeholder="https://www.youtube.com/watch?v=..."
						disabled={isLoading}
						class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
					/>
					<button
						on:click={handleAnalyze}
						disabled={isLoading || !youtubeUrl.trim()}
						class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
					>
						{#if isLoading}
							<div class="flex items-center gap-2">
								<svg class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
									<circle
										class="opacity-25"
										cx="12"
										cy="12"
										r="10"
										stroke="currentColor"
										stroke-width="4"
									></circle>
									<path
										class="opacity-75"
										fill="currentColor"
										d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
									></path>
								</svg>
								Analyzing...
							</div>
						{:else}
							{mode === 'summarizer' ? 'Summarize' : 'Explain'}
						{/if}
					</button>
				</div>
			</div>

			<!-- Video Preview -->
			{#if thumbnailUrl && youtubeUrl.trim()}
				<div class="bg-white border border-gray-200 rounded-lg p-6 mb-6">
					<h3 class="text-lg font-medium text-gray-900 mb-4">Video Preview</h3>
					<div class="flex gap-4">
						<img
							src={thumbnailUrl}
							alt="Video thumbnail"
							class="w-32 h-18 object-cover rounded-lg"
							on:error={(e) => {
								e.target.src = 'https://img.youtube.com/vi/' + videoId + '/hqdefault.jpg';
							}}
						/>
						<div class="flex-1">
							<p class="text-sm text-gray-600">Ready to analyze this video</p>
							<div class="mt-2">
								<span
									class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
								>
									Video detected
								</span>
							</div>
						</div>
					</div>
				</div>
			{/if}

			<!-- Error Message -->
			{#if error}
				<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
					<div class="flex items-start">
						<svg
							class="w-5 h-5 text-red-400 mt-0.5 mr-3"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
							/>
						</svg>
						<div>
							<h3 class="text-sm font-medium text-red-800">Error</h3>
							<p class="text-sm text-red-700 mt-1">{error}</p>
						</div>
					</div>
				</div>
			{/if}

			<!-- Loading State -->
			{#if isLoading}
				<div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
					<div class="flex items-center">
						<svg class="w-5 h-5 text-blue-500 animate-spin mr-3" fill="none" viewBox="0 0 24 24">
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							></circle>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
							></path>
						</svg>
						<div>
							<h3 class="text-sm font-medium text-blue-800">
								{mode === 'summarizer' ? 'Generating Summary' : 'Creating Explanation'}
							</h3>
							<p class="text-sm text-blue-700">
								{mode === 'summarizer'
									? 'Analyzing video content and creating a concise summary...'
									: 'Analyzing video content and preparing a detailed explanation...'}
							</p>
						</div>
					</div>
				</div>
			{/if}

			<!-- Results -->
			{#if result && !isLoading}
				<div class="bg-white border border-gray-200 rounded-lg p-6">
					<div class="flex items-start justify-between mb-4">
						<h3 class="text-lg font-medium text-gray-900">
							{mode === 'summarizer' ? 'Summary' : 'Detailed Explanation'}
						</h3>
						<button
							on:click={() => navigator.clipboard.writeText(result)}
							class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
							title="Copy to clipboard"
						>
							<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
								/>
							</svg>
						</button>
					</div>
					<div class="prose prose-sm max-w-none text-gray-800">
						{@html marked.parse(result)}
					</div>
				</div>
			{/if}

			<!-- Usage Tips -->
			{#if !result && !isLoading && !error}
				<div class="bg-gray-50 border border-gray-200 rounded-lg p-6">
					<h3 class="text-lg font-medium text-gray-900 mb-4">How to use</h3>
					<div class="space-y-3">
						<div class="flex items-start gap-3">
							<div
								class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
							>
								<span class="text-xs font-medium text-blue-600">1</span>
							</div>
							<div>
								<p class="font-medium text-gray-900">Paste YouTube URL</p>
								<p class="text-sm text-gray-600">
									Copy and paste any YouTube video URL into the input field above
								</p>
							</div>
						</div>
						<div class="flex items-start gap-3">
							<div
								class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
							>
								<span class="text-xs font-medium text-blue-600">2</span>
							</div>
							<div>
								<p class="font-medium text-gray-900">
									Click {mode === 'summarizer' ? 'Summarize' : 'Explain'}
								</p>
								<p class="text-sm text-gray-600">
									{mode === 'summarizer'
										? 'Get a concise overview of the video content'
										: 'Get detailed explanations with examples and context'}
								</p>
							</div>
						</div>
						<div class="flex items-start gap-3">
							<div
								class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
							>
								<span class="text-xs font-medium text-blue-600">3</span>
							</div>
							<div>
								<p class="font-medium text-gray-900">Review and copy</p>
								<p class="text-sm text-gray-600">
									Read the AI-generated content and copy it if needed
								</p>
							</div>
						</div>
					</div>
				</div>
			{/if}
		</div>
	</div>
</div>
