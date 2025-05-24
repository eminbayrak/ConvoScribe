<script lang="ts">
	export let activeTab: 'summarizer' | 'chat';
	export let onTabChange: (tab: 'summarizer' | 'chat') => void;
</script>

<div class="flex border-b mb-6">
	<button
		class="px-6 py-3 text-sm font-medium border-b-2 transition-colors {activeTab === 'summarizer'
			? 'border-blue-500 text-blue-600'
			: 'border-transparent text-gray-500 hover:text-gray-700'}"
		on:click={() => onTabChange('summarizer')}
	>
		Summarizer & Explainer
	</button>
	<button
		class="px-6 py-3 text-sm font-medium border-b-2 transition-colors {activeTab === 'chat'
			? 'border-blue-500 text-blue-600'
			: 'border-transparent text-gray-500 hover:text-gray-700'}"
		on:click={() => onTabChange('chat')}
	>
		Chat with AI
	</button>
</div>
