<script lang="ts">
  import type maplibregl from 'maplibre-gl';

  export let map: maplibregl.Map | null = null;

  const IDEE_SOURCE_ID = 'idee-landcover';
  const IDEE_LAYER_ID  = 'idee-landcover-layer';
  const IDEE_TILE_URL  =
    'https://servicios.idee.es/wmts/ocupacion-suelo?' +
    'SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0' +
    '&LAYER=LC.LandCoverSurfaces' +
    '&STYLE=LC.LandCoverSurfaces.Default' +
    '&TILEMATRIXSET=GoogleMapsCompatible' +
    '&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}' +
    '&FORMAT=image%2Fpng';

  type BaseKey = 'carto' | 'landcover';

  let activeBase: BaseKey = 'carto';
  let ideeReady = false;

  // Añade la capa IDEE sobre Positron (solo la primera vez)
  function ensureIdeeLayer() {
    if (!map || ideeReady) return;
    if (!map.getSource(IDEE_SOURCE_ID)) {
      map.addSource(IDEE_SOURCE_ID, {
        type: 'raster',
        tiles: [IDEE_TILE_URL],
        tileSize: 256,
        minzoom: 0,
        maxzoom: 17,
        attribution: '© <a href="https://www.idee.es" target="_blank">IDEE / IGN España</a> (CC BY 4.0)'
      });
    }
    if (!map.getLayer(IDEE_LAYER_ID)) {
      map.addLayer({
        id: IDEE_LAYER_ID,
        type: 'raster',
        source: IDEE_SOURCE_ID,
        layout: { visibility: 'none' },
        paint: { 'raster-opacity': 1 }
      });
    }
    ideeReady = true;
  }

  function switchBase(key: BaseKey) {
    if (!map || key === activeBase) return;

    if (key === 'landcover') {
      // Asegurar que la capa IDEE existe antes de mostrarla
      if (map.isStyleLoaded()) {
        ensureIdeeLayer();
        map.setLayoutProperty(IDEE_LAYER_ID, 'visibility', 'visible');
      } else {
        map.once('style.load', () => {
          ensureIdeeLayer();
          map!.setLayoutProperty(IDEE_LAYER_ID, 'visibility', 'visible');
        });
      }
    } else {
      // Ocultar IDEE: Positron queda como único mapa
      if (ideeReady && map.getLayer(IDEE_LAYER_ID)) {
        map.setLayoutProperty(IDEE_LAYER_ID, 'visibility', 'none');
      }
    }

    activeBase = key;
  }

  const LABELS: Record<BaseKey, { label: string; icon: string }> = {
    carto:     { label: 'Positron',  icon: '🗺️' },
    landcover: { label: 'Suelo',     icon: '🌿' }
  };

  const baseKeys: BaseKey[] = ['carto', 'landcover'];
</script>

<div class="base-switcher" role="group" aria-label="Mapa base">
  <div class="switcher-header">
    <svg class="layers-icon" xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polygon points="12 2 2 7 12 12 22 7 12 2"/>
      <polyline points="2 17 12 22 22 17"/>
      <polyline points="2 12 12 17 22 12"/>
    </svg>
    <span class="header-label">Mapa base</span>
  </div>
  <div class="divider"></div>

  {#each baseKeys as key}
    <button
      id="base-btn-{key}"
      class="base-btn"
      class:active={activeBase === key}
      on:click={() => switchBase(key)}
      aria-pressed={activeBase === key}
      title={LABELS[key].label}
    >
      <span class="icon">{LABELS[key].icon}</span>
      <span class="label">{LABELS[key].label}</span>
    </button>
  {/each}
</div>

<style>
  .base-switcher {
    position: absolute;
    bottom: 1.5rem;
    right: 0.75rem;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    z-index: 10;
    background: rgba(12, 12, 20, 0.72);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 0.4rem;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.35);
  }

  .switcher-header {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0 0.15rem 0.1rem;
    color: rgba(255, 255, 255, 0.35);
  }

  .layers-icon { flex-shrink: 0; opacity: 0.7; }

  .header-label {
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    white-space: nowrap;
    font-family: 'Inter', system-ui, sans-serif;
  }

  .divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.08);
    margin: 0 0 0.1rem;
  }

  .base-btn {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.55rem;
    border: 1px solid transparent;
    border-radius: 7px;
    background: transparent;
    color: rgba(255, 255, 255, 0.45);
    cursor: pointer;
    transition: all 0.18s ease;
    font-family: 'Inter', system-ui, sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    white-space: nowrap;
  }

  .base-btn:hover:not(.active) {
    background: rgba(255, 255, 255, 0.07);
    color: rgba(255, 255, 255, 0.8);
  }

  .base-btn.active {
    background: rgba(0, 255, 204, 0.12);
    color: #00ffcc;
    border-color: rgba(0, 255, 204, 0.3);
  }

  .icon { font-size: 0.85rem; line-height: 1; flex-shrink: 0; }

  @media (max-width: 480px) {
    .base-switcher { bottom: 1rem; right: 0.5rem; }
    .base-btn { padding: 0.4rem; justify-content: center; }
    .label { display: none; }
    .icon { font-size: 1rem; }
    .header-label { display: none; }
  }
</style>
