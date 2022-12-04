<script lang="ts">
    export let active = false;
</script>

<button
    on:click
    class="w-6 h-6 border bg-white rounded text-sm inline-flex justify-center items-center"
    class:border-blue-500={active}
>
    <slot />
</button>
