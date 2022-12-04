<script lang="ts">
    import { FILTERED_KEYS, server } from "$lib/connection";

    $: stateText = JSON.stringify(filter($server.state), null, 2);

    function filter(state: any) {
        const newState = { ...state };

        for (const key of FILTERED_KEYS) {
            if (newState[key] instanceof Array) {
                newState[key] = "<filtered>";
            }
        }

        return newState;
    }
</script>

<h2 class="mt-8 mb-2 pl-2 text-2xl font-bold">State</h2>
<pre
    class="max-h-96 p-2 bg-gray-100 rounded font-mono overflow-x-auto overflow-y-auto text-sm">{stateText}</pre>
