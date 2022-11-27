<script lang="ts">
    import Map from "$lib/components/map/Map.svelte";
    import Sidebar from "$lib/components/Sidebar.svelte";
</script>

<div class="min-h-screen grid grid-cols-5">
    <div class="col-span-2 border-r">
        <Sidebar />
    </div>

    <div class="col-span-3 flex justify-center items-center bg-gray-50">
        <Map />
    </div>
</div>
