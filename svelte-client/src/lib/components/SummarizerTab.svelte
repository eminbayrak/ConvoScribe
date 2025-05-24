<script lang="ts">
	export let youtubeUrl: string;
	export let onSummarize: () => void;
	export let onExplain: () => void;
	export let isLoading: boolean;
	export let errorMessage: string;
	export let summaryResult: string;
	export let explanationResult: string;
	export let showSummary: boolean;
	export let showExplanation: boolean;
</script>

<div class="space-y-6">
	<p class="text-gray-600 text-center">
		Enter a YouTube video URL to get a summary or a detailed explanation.
	</p>

	<!-- URL Input -->
	<div class="flex gap-3">
		<input
			type="text"
			bind:value={youtubeUrl}
			placeholder="Enter YouTube Video URL"
			class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
		/>
	</div>

	<!-- Action Buttons -->
	<div class="flex gap-3 justify-center">
		<button
			on:click={onSummarize}
			disabled={isLoading}
			class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
		>
			Get Summary
		</button>
		<button
			on:click={onExplain}
			disabled={isLoading}
			class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
		>
			Get Detailed Explanation
		</button>
	</div>

	<!-- Loading Indicator -->
	{#if isLoading}
		<div class="text-center text-blue-600 py-4">
			<div
				class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-2"
			></div>
			Processing...
		</div>
	{/if}

	<!-- Error Message -->
	{#if errorMessage}
		<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
			{errorMessage}
		</div>
	{/if}

	<!-- Summary Result -->
	{#if showSummary && summaryResult}
		<div class="bg-gray-50 border border-gray-200 rounded-lg p-6">
			<h2 class="text-xl font-semibold mb-4 text-gray-800">Summary</h2>
			<div class="prose max-w-none text-gray-700 whitespace-pre-wrap">
				{summaryResult}
			</div>
		</div>
	{/if}

	<!-- Explanation Result -->
	{#if showExplanation && explanationResult}
		<div class="bg-gray-50 border border-gray-200 rounded-lg p-6 mt-6">
			<h2 class="text-xl font-semibold mb-4 text-gray-800">Detailed Explanation</h2>
			<div class="prose max-w-none text-gray-700 whitespace-pre-wrap">
				{explanationResult}
			</div>
		</div>
	{/if}
</div>
