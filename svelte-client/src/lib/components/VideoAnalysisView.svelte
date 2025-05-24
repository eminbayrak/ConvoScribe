<script lang="ts">
	import { marked } from '../markdown.js';

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

<div class="flex flex-col h-full bg-theme-primary">
	<!-- Header -->
	<div class="p-6 border-b border-theme-primary">
		<div class="max-w-4xl mx-auto">
			<h1 class="text-2xl font-semibold text-theme-primary mb-2">
				{mode === 'summarizer' ? 'Video Summarizer' : 'Video Explainer'}
			</h1>
			<p class="text-theme-secondary">
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
			<div class="bg-theme-primary border border-theme-primary rounded-lg p-6 mb-6">
				<label for="youtube-url" class="block text-sm font-medium text-theme-primary mb-3">
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
						class="flex-1 px-4 py-3 border border-theme-primary rounded-lg focus:ring-2 focus:border-theme-focus focus:border-transparent disabled:opacity-50 bg-theme-primary text-theme-primary"
					/>
					<button
						on:click={handleAnalyze}
						disabled={isLoading || !youtubeUrl.trim()}
						class="px-6 py-3 bg-btn-primary hover:bg-btn-primary focus:ring-2 focus:border-theme-focus disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium rounded-lg"
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
				<div class="bg-theme-primary border border-theme-primary rounded-lg p-6 mb-6">
					<h3 class="text-lg font-medium text-theme-primary mb-4">Video Preview</h3>
					<div class="flex gap-4">
						<img
							src={thumbnailUrl}
							alt="Video thumbnail"
							class="w-32 h-18 object-cover rounded-lg"
							on:error={(e) => {
								const target = e.target as HTMLImageElement;
								if (target) {
									target.src = 'https://img.youtube.com/vi/' + videoId + '/hqdefault.jpg';
								}
							}}
						/>
						<div class="flex-1">
							<p class="text-sm text-theme-secondary">Ready to analyze this video</p>
							<div class="mt-2">
								<span
									class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-status-success text-white"
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
				<div class="bg-status-error border border-theme-primary rounded-lg p-4 mb-6">
					<div class="flex items-start">
						<svg
							class="w-5 h-5 text-white mt-0.5 mr-3"
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
							<h3 class="text-sm font-medium text-white">Error</h3>
							<p class="text-sm text-white mt-1">{error}</p>
						</div>
					</div>
				</div>
			{/if}

			<!-- Loading State -->
			{#if isLoading}
				<div class="bg-status-info border border-theme-primary rounded-lg p-6 mb-6">
					<div class="flex items-center">
						<svg class="w-5 h-5 text-white animate-spin mr-3" fill="none" viewBox="0 0 24 24">
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
							<h3 class="text-sm font-medium text-white">
								{mode === 'summarizer' ? 'Generating Summary' : 'Creating Explanation'}
							</h3>
							<p class="text-sm text-white">
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
				<div class="bg-theme-primary border border-theme-primary rounded-lg p-6">
					<div class="flex items-start justify-between mb-4">
						<h3 class="text-lg font-medium text-theme-primary">
							{mode === 'summarizer' ? 'Summary' : 'Detailed Explanation'}
						</h3>
						<button
							on:click={() => navigator.clipboard.writeText(result)}
							class="p-2 text-theme-muted hover:text-theme-secondary rounded-lg hover:bg-theme-secondary"
							title="Copy to clipboard"
							aria-label="Copy to clipboard"
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
					<div class="prose-themed prose-sm max-w-none">
						{@html marked.parse(result)}
					</div>
				</div>
			{/if}

			<!-- Usage Tips -->
			{#if !result && !isLoading && !error}
				<div class="bg-theme-secondary border border-theme-primary rounded-lg p-6">
					<h3 class="text-lg font-medium text-theme-primary mb-4">How to use</h3>
					<div class="space-y-3">
						<div class="flex items-start gap-3">
							<div
								class="w-6 h-6 bg-btn-primary rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
							>
								<span class="text-xs font-medium text-white">1</span>
							</div>
							<div>
								<p class="font-medium text-theme-primary">Paste YouTube URL</p>
								<p class="text-sm text-theme-secondary">
									Copy and paste any YouTube video URL into the input field above
								</p>
							</div>
						</div>
						<div class="flex items-start gap-3">
							<div
								class="w-6 h-6 bg-btn-primary rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
							>
								<span class="text-xs font-medium text-white">2</span>
							</div>
							<div>
								<p class="font-medium text-theme-primary">
									Click {mode === 'summarizer' ? 'Summarize' : 'Explain'}
								</p>
								<p class="text-sm text-theme-secondary">
									{mode === 'summarizer'
										? 'Get a concise overview of the video content'
										: 'Get detailed explanations with examples and context'}
								</p>
							</div>
						</div>
						<div class="flex items-start gap-3">
							<div
								class="w-6 h-6 bg-btn-primary rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
							>
								<span class="text-xs font-medium text-white">3</span>
							</div>
							<div>
								<p class="font-medium text-theme-primary">Review and copy</p>
								<p class="text-sm text-theme-secondary">
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
