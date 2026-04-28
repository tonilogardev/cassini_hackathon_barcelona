<script lang="ts">
  import { onMount } from 'svelte';
  import maplibregl from 'maplibre-gl';
  import 'maplibre-gl/dist/maplibre-gl.css';
  import { Protocol } from 'pmtiles';
  import Branding from './components/Branding.svelte';
  import BaseSwitcher from './components/BaseSwitcher.svelte';
  import ColorLegend from './components/ColorLegend.svelte';
  import PlaceViewer from './components/PlaceViewer.svelte';

  // Registrar protocolo PMTiles globalmente (antes de crear el mapa)
  const protocol = new Protocol();
  maplibregl.addProtocol('pmtiles', protocol.tile.bind(protocol));

  let mapContainer: HTMLDivElement;
  let map: maplibregl.Map;

  onMount(() => {
    map = new maplibregl.Map({
      container: mapContainer,
      style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
      center: [1.5218, 41.5912], // Coordenadas de Cataluña
      zoom: 7
    });

    return () => map.remove();
  });
</script>

<main>
  <Branding />
  <BaseSwitcher {map} />
  <ColorLegend />
  <PlaceViewer {map} />
  <div class="map-container" bind:this={mapContainer}></div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    overflow: hidden;
  }

  .map-container {
    width: 100%;
    height: 100vh;
    position: absolute;
    top: 0;
    left: 0;
  }
</style>