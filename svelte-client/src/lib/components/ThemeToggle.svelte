<script lang="ts">
	import { themeMode, toggleTheme } from '$lib/themeStore';

	function handleToggle() {
		toggleTheme();
	}

	function getThemeIcon(mode: 'light' | 'dark') {
		if (mode === 'dark') {
			return {
				icon: 'moon',
				label: 'Dark mode'
			};
		} else {
			return {
				icon: 'sun',
				label: 'Light mode'
			};
		}
	}

	$: themeInfo = getThemeIcon($themeMode);
</script>

<button
	on:click={handleToggle}
	class="flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-sidebar-muted hover:bg-sidebar-hover hover:text-sidebar"
	title="Toggle theme ({themeInfo.label})"
>
	{#if themeInfo.icon === 'sun'}
		<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
			/>
		</svg>
	{:else}
		<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
			/>
		</svg>
	{/if}
	<span class="text-sm">{themeInfo.label}</span>
</button>
