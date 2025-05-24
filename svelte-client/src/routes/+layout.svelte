<script lang="ts">
	import '../app.css';
	import ThemeProvider from '$lib/components/ThemeProvider.svelte';

	let { children } = $props();
</script>

<ThemeProvider />
{@render children()}
