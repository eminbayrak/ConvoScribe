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
	<!-- Content Area -->
	<div class="flex-1 overflow-y-auto">
		<div class="max-w-3xl mx-auto p-6">
			<!-- URL Input Section -->
			<div class="mb-6">
				<h1 class="text-xl font-medium text-theme-primary mb-4">
					{mode === 'summarizer' ? 'Video Summarizer' : 'Video Explainer'}
				</h1>
				<div class="relative">
					<input
						type="url"
						bind:value={youtubeUrl}
						on:keypress={handleKeypress}
						placeholder="Paste YouTube URL here..."
						disabled={isLoading}
						class="w-full pl-4 pr-32 py-4 border border-theme-primary rounded-3xl focus:ring-1 focus:ring-blue-500 focus:border-theme-focus disabled:opacity-50 bg-theme-secondary text-theme-primary shadow-sm focus:shadow-md transition-shadow"
					/>
					<button
						on:click={handleAnalyze}
						disabled={isLoading || !youtubeUrl.trim()}
						class="absolute right-2 top-2 bottom-2 px-6 bg-btn-primary hover:bg-btn-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium rounded-2xl"
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
								Analyzing
							</div>
						{:else}
							{mode === 'summarizer' ? 'Summarize' : 'Explain'}
						{/if}
					</button>
				</div>
			</div>

			{#if error}
				<div class="bg-status-error bg-opacity-10 border border-status-error rounded-lg p-4 mb-6">
					<div class="flex items-start">
						<svg
							class="w-5 h-5 text-status-error mt-0.5 mr-3"
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
							<h3 class="text-sm font-medium text-status-error">Error</h3>
							<p class="text-sm text-status-error opacity-80 mt-1">{error}</p>
						</div>
					</div>
				</div>
			{/if}

			<!-- Loading State -->
			{#if isLoading}
				<div class="bg-status-info bg-opacity-10 border border-status-info rounded-lg p-4 mb-6">
					<div class="flex items-center">
						<svg class="w-5 h-5 text-status-info animate-spin mr-3" fill="none" viewBox="0 0 24 24">
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
							<h3 class="text-sm font-medium text-status-info">
								{mode === 'summarizer' ? 'Generating Summary' : 'Creating Explanation'}
							</h3>
						</div>
					</div>
				</div>
			{/if}

			<!-- Video Preview -->
			{#if videoId && thumbnailUrl}
				<div class="mb-6">
					<div class="bg-theme-secondary border border-theme-primary rounded-lg p-4">
						<h3 class="text-sm font-medium text-theme-primary mb-3">Video Preview</h3>
						<div class="relative inline-block">
							<img
								src={thumbnailUrl}
								alt="YouTube video thumbnail"
								class="w-64 h-36 object-cover rounded-lg border border-theme-primary"
								on:error={() => {
									// Fallback to default thumbnail if maxresdefault fails
									if (thumbnailUrl?.includes('maxresdefault')) {
										thumbnailUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
									}
								}}
							/>
							<div class="absolute inset-0 flex items-center justify-center">
								<div
									class="w-12 h-12 bg-black bg-opacity-70 rounded-full flex items-center justify-center"
								>
									<svg class="w-6 h-6 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
										<path d="M8 5v14l11-7z" />
									</svg>
								</div>
							</div>
						</div>
					</div>
				</div>
			{/if}

			<!-- Results -->
			{#if result && !isLoading}
				<div class="bg-theme-secondary border border-theme-primary rounded-lg p-6">
					<div class="flex items-start justify-between mb-4">
						<h3 class="text-lg font-medium text-theme-primary">
							{mode === 'summarizer' ? 'Summary' : 'Explanation'}
						</h3>
						<button
							on:click={() => navigator.clipboard.writeText(result)}
							class="p-2 text-theme-secondary hover:text-theme-primary rounded-lg hover:bg-theme-tertiary"
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
					<div class="prose prose-lg max-w-none text-theme-secondary leading-relaxed">
						{@html marked.parse(result)}
					</div>
				</div>
			{/if}
		</div>
	</div>
</div>
