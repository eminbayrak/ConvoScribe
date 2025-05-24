<script lang="ts">
	import { onMount } from 'svelte';
	import { currentTheme, themeMode, applyTheme } from '$lib/themeStore';

	// Apply theme whenever it changes
	$: if ($currentTheme) {
		applyTheme($currentTheme);
	}

	onMount(() => {
		// Apply initial theme
		applyTheme($currentTheme);
	});
</script>

<!-- This component doesn't render anything, it just applies the theme -->
