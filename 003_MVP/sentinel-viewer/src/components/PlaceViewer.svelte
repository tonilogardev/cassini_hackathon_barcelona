<script lang="ts">
  import { onMount } from 'svelte';
  import type maplibregl from 'maplibre-gl';
  import { PMTiles } from 'pmtiles';

  export let map: maplibregl.Map | null = null;

  // ─── Types ────────────────────────────────────────────────────────────────
  type PlaceKey = string;
  type Manifest = Record<PlaceKey, string[]>;

  // ─── State ────────────────────────────────────────────────────────────────
  let manifest   : Manifest = {};
  let places     : PlaceKey[] = [];
  let place      : PlaceKey = '';   // sin selección inicial
  let activeFile : string | null = null;
  let isOpen     = true;
  let loading    = false;

  // ─── Load manifest ────────────────────────────────────────────────────────
  onMount(async () => {
    const res = await fetch('/images/places/manifest.json');
    manifest  = await res.json() as Manifest;
    places    = Object.keys(manifest);
    // No pre-seleccionamos ningún lugar: el usuario elige explícitamente
  });

  // ─── Derived ──────────────────────────────────────────────────────────────

  // Agrupa los ficheros de la zona activa por fecha (primeros 8 caracteres)
  $: grouped = (() => {
    const files = manifest[place] ?? [];
    const map: Record<string, string[]> = {};
    for (const f of files) {
      const date = f.slice(0, 8);
      (map[date] ??= []).push(f);
    }
    return Object.entries(map);          // [['20200126', [...]], ...]
  })();

  $: activeDate = activeFile ? fmtDate(activeFile.slice(0, 8)) : null;

  // ─── Helpers ──────────────────────────────────────────────────────────────
  function fmtDate(d: string): string {
    const m = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
    return `${parseInt(d.slice(6,8))} ${m[parseInt(d.slice(4,6))-1]} ${d.slice(0,4)}`;
  }

  // ─── Map ops ──────────────────────────────────────────────────────────────
  const SRC = 'pv-src';
  const LYR = 'pv-lyr';

  // Forzar que la capa esté siempre arriba
  function moveLayerToTop() {
    if (map && map.getLayer(LYR)) {
      map.moveLayer(LYR);
    }
  }

  // Escuchar cambios de estilo (mapa base) para re-posicionar nuestra capa
  onMount(() => {
    const handleResize = () => map?.resize();
    window.addEventListener('resize', handleResize);
    
    map?.on('style.load', moveLayerToTop);

    return () => {
      window.removeEventListener('resize', handleResize);
      map?.off('style.load', moveLayerToTop);
    };
  });

  function clearLayer() {
    if (!map) return;
    if (map.getLayer(LYR)) map.removeLayer(LYR);
    if (map.getSource(SRC)) map.removeSource(SRC);
  }

  async function selectPlace(p: PlaceKey) {
    if (p === place) return;
    clearLayer();
    activeFile = null;
    place = p;
    loading = true;
    try {
      const ref = `${manifest[p][0]}`;
      const pt  = new PMTiles(`/images/places/${p}/${ref}.pmtiles`);
      const h   = await pt.getHeader();
      
      const isMobile = window.innerWidth < 600;
      map?.fitBounds([[h.minLon, h.minLat], [h.maxLon, h.maxLat]],
        { padding: isMobile ? 20 : 60, duration: 1200, maxZoom: 14 });
    } catch { /* bounds no disponibles */ }
    loading = false;
  }

  function selectImage(file: string) {
    if (!map) return;
    if (activeFile === file) { clearLayer(); activeFile = null; return; }
    clearLayer();
    map.addSource(SRC, {
      type: 'raster',
      url: `pmtiles:///images/places/${place}/${file}.pmtiles`,
      tileSize: 256
    });
    map.addLayer({ id: LYR, type: 'raster', source: SRC });
    activeFile = file;
    moveLayerToTop(); // Asegurar que sale encima de IDEE u otros
  }
</script>

<div class="pv-wrap">

  <!-- Toggle -->
  <button
    class="pv-toggle"
    class:open={isOpen}
    on:click={() => (isOpen = !isOpen)}
    aria-expanded={isOpen}
    title={isOpen ? 'Minimizar' : 'Explorador de zonas'}
  >
    <span>Zonas</span>
    {#if activeDate && !isOpen}
      <span class="pv-chip">{activeDate}</span>
    {/if}
    <svg
      class="pv-chevron"
      class:rotated={isOpen}
      xmlns="http://www.w3.org/2000/svg"
      width="10" height="10"
      viewBox="0 0 24 24"
      fill="none" stroke="currentColor"
      stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"
    >
      <polyline points="18 15 12 9 6 15"/>
    </svg>
  </button>

  <!-- Panel -->
  {#if isOpen}
    <div class="pv-panel">

      <!-- Place selector -->
      <p class="pv-label">Zona</p>
      <div class="pv-places">
        {#each places as pk}
          <button
            class="pv-place"
            class:active={place === pk}
            disabled={loading}
            on:click={() => selectPlace(pk)}
          >{pk}</button>
        {/each}
      </div>

      {#if place}
      <div class="pv-hr"></div>

      <!-- Image list: visible solo cuando hay zona seleccionada -->
      <p class="pv-label">
        Imágenes
        {#if activeDate}<span class="pv-chip">{activeDate}</span>{/if}
      </p>

      <div class="pv-images">
        {#each grouped as [date, files]}
          <p class="pv-date">{fmtDate(date)}</p>
          {#each files as file}
            <button
              class="pv-img"
              class:active={activeFile === file}
              on:click={() => selectImage(file)}
              title={file}
            >
              <span class="pv-filename">{file}</span>
              {#if activeFile === file}<span class="pv-dot"></span>{/if}
            </button>
          {/each}
        {/each}
      </div>
      {/if}

    </div>
  {/if}

</div>

<style>
  .pv-wrap {
    position: absolute;
    top: 1rem; right: 0.75rem;
    bottom: 8rem;
    display: flex; flex-direction: column; align-items: flex-end;
    gap: 0.3rem; z-index: 10;
    font-family: 'Inter', system-ui, sans-serif;
  }

  /* Toggle */
  .pv-toggle {
    flex-shrink: 0;
    display: flex; align-items: center; gap: 0.4rem;
    padding: 0.38rem 0.7rem;
    background: rgba(10,10,11,.80); backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,.1); border-radius: 8px;
    color: rgba(255,255,255,.5); cursor: pointer;
    font: 600 0.68rem/1 inherit; text-transform: uppercase; letter-spacing: .07em;
    box-shadow: 0 2px 8px rgba(0,0,0,.3); transition: all .15s ease;
  }
  .pv-toggle:hover       { color: rgba(255,255,255,.85); border-color: rgba(255,255,255,.2); }
  .pv-toggle.open        { color: #00ffcc; border-color: rgba(0,255,204,.3); background: rgba(0,255,204,.07); }

  .pv-chevron { transition: transform .2s ease; opacity: .6; flex-shrink: 0; }
  .pv-chevron.rotated { transform: rotate(180deg); }

  /* Panel */
  .pv-panel {
    width: 220px;
    flex: 0 1 auto;      /* No se estira, pero puede encogerse */
    max-height: 100%;    /* No sobrepasa el límite del wrapper (bottom: 8rem) */
    min-height: 0;
    overflow-y: auto;
    background: rgba(10,10,11,.85); backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,.08); border-radius: 10px;
    padding: 0.65rem 0.6rem; box-shadow: 0 6px 24px rgba(0,0,0,.5);
    animation: fadeIn .18s ease;
  }
  .pv-panel::-webkit-scrollbar { width: 3px; }
  .pv-panel::-webkit-scrollbar-thumb { background: rgba(255,255,255,.1); border-radius: 2px; }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(-4px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  /* Labels */
  .pv-label {
    margin: 0 0 .35rem; font-size: .58rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: .09em;
    color: rgba(255,255,255,.28);
    display: flex; align-items: center; gap: .4rem;
  }
  .pv-hr   { height: 1px; background: rgba(255,255,255,.06); margin: .5rem 0; }

  /* Chip */
  .pv-chip {
    background: rgba(0,255,204,.12); color: #00ffcc;
    border: 1px solid rgba(0,255,204,.25); border-radius: 4px;
    padding: .05rem .35rem; font-size: .58rem; font-weight: 700;
    text-transform: none; letter-spacing: 0;
  }

  /* Places */
  .pv-places { display: flex; flex-direction: column; gap: .2rem; }

  .pv-place {
    padding: .35rem .5rem; border: 1px solid transparent; border-radius: 6px;
    background: transparent; color: rgba(255,255,255,.45);
    cursor: pointer; font: 500 .75rem/1 inherit; text-align: left;
    transition: all .14s ease;
  }
  .pv-place:hover:not(.active):not(:disabled) { background: rgba(255,255,255,.05); color: rgba(255,255,255,.8); }
  .pv-place.active  { color: #00ffcc; border-color: rgba(0,255,204,.25); background: rgba(0,255,204,.08); }
  .pv-place:disabled { opacity: .35; cursor: wait; }

  /* Images */
  .pv-images { display: flex; flex-direction: column; gap: .1rem; }

  .pv-date {
    margin: .45rem 0 .15rem; font-size: .6rem; font-weight: 700;
    color: rgba(255,255,255,.2);
    padding-bottom: .1rem; border-bottom: 1px solid rgba(255,255,255,.05);
  }

  .pv-img {
    display: flex; align-items: center; justify-content: space-between;
    width: 100%; padding: .28rem .45rem;
    border: 1px solid transparent; border-radius: 5px;
    background: transparent; color: rgba(255,255,255,.4);
    cursor: pointer; font: 400 .68rem/1.3 inherit; text-align: left;
    transition: all .13s ease;
  }
  .pv-img:hover:not(.active) { background: rgba(255,255,255,.04); color: rgba(255,255,255,.75); }
  .pv-img.active { color: #00ffcc; border-color: rgba(0,255,204,.22); background: rgba(0,255,204,.07); font-weight: 600; }

  .pv-filename { flex: 1; word-break: break-all; }

  .pv-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #00ffcc; box-shadow: 0 0 5px #00ffcc; flex-shrink: 0;
  }

  /* Responsive */
  @media (max-width: 600px) {
    .pv-wrap {
      top: auto;
      bottom: 1.5rem;    /* Pegado al BaseSwitcher para ahorrar espacio */
      right: 0.5rem;
      height: auto;
      max-height: 80vh;  /* Ocupar hasta el 80% de la pantalla */
      flex-direction: column-reverse; /* CRECE HACIA ARRIBA */
    }

    .pv-panel {
      width: min(220px, calc(100vw - 1rem));
      margin-bottom: 0.3rem; /* Espacio con el botón que ahora está debajo */
    }

    .pv-toggle span:first-child { display: none; }
  }
</style>
