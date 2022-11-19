<script lang="ts">
    import { events } from "$lib/connection";
    import Map from "$lib/Map.svelte";

    $: e = $events;

    $: time = e.state.computationTime as number | undefined;
</script>

<div class="min-h-screen grid grid-cols-5">
    <div class="px-6 py-3 col-span-2 border-r">
        <h2 class="mb-2 text-lg font-bold">Messages</h2>

        <div>
            {#each e.msgs as msg}
                <div class="my-1 p-2 border overflow-x-auto rounded">
                    <pre>{JSON.stringify(msg)}</pre>
                </div>
            {/each}
        </div>

        {#if time}
            <div class="mt-2">
                Computation time: {time} s
            </div>
        {/if}
    </div>

    <div class="col-span-3 flex justify-center items-center bg-gray-50">
        <Map />
    </div>
</div>
