<script lang="ts">
  let isOpen = true; // Visible por defecto para que el usuario lea la leyenda

  const items = [
    { id: 1, color: '#2196F3', label: 'Agua sin anomalías' },
    { id: 2, color: '#E8430F', label: 'Alta turbidez / Sedimentos' },
    { id: 3, color: '#BEFF6B', label: 'Alta clorofila (Fitoplancton)' },
    { id: 4, color: '#1B8A0A', label: 'Algas superficiales (Bloom)' },
    { id: 5, color: '#7A0000', label: 'Posible contaminación / Puntos anómalos' }
  ];

  function toggle() {
    isOpen = !isOpen;
  }
</script>

<div class="legend-wrapper">
  <!-- Botón para mostrar/ocultar siempre visible -->
  <button
    class="legend-toggle"
    class:is-open={isOpen}
    on:click={toggle}
    aria-expanded={isOpen}
    aria-label={isOpen ? 'Ocultar leyenda' : 'Mostrar leyenda de calidad del agua'}
    title={isOpen ? 'Ocultar leyenda' : 'Leyenda'}
  >
    <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <line x1="8" y1="6" x2="21" y2="6"/>
      <line x1="8" y1="12" x2="21" y2="12"/>
      <line x1="8" y1="18" x2="21" y2="18"/>
      <line x1="3" y1="6" x2="3.01" y2="6"/>
      <line x1="3" y1="12" x2="3.01" y2="12"/>
      <line x1="3" y1="18" x2="3.01" y2="18"/>
    </svg>
    <span class="toggle-label">Leyenda</span>
    <svg
      class="chevron"
      class:rotated={isOpen}
      xmlns="http://www.w3.org/2000/svg"
      width="10" height="10"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2.5"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <polyline points="18 15 12 9 6 15"/>
    </svg>
  </button>

  <!-- Panel desplegable -->
  {#if isOpen}
    <div class="legend-panel" role="region" aria-label="Leyenda de calidad del agua">
      <p class="legend-title">Calidad del Agua</p>
      <ul class="legend-list">
        {#each items as item}
          <li class="legend-item">
            <span
              class="color-swatch"
              style="background-color: {item.color};"
              aria-hidden="true"
            ></span>
            <span class="item-label">
              <span class="item-num">{item.id}</span>
              {item.label}
            </span>
          </li>
        {/each}
      </ul>
    </div>
  {/if}
</div>

<style>
  .legend-wrapper {
    position: absolute;
    bottom: 1.5rem;
    left: 0.75rem;
    display: flex;
    flex-direction: column-reverse; /* Panel crece hacia arriba */
    gap: 0.3rem;
    z-index: 10;
    font-family: 'Inter', system-ui, sans-serif;
    align-items: flex-start;
  }

  /* --- Botón toggle --- */
  .legend-toggle {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.38rem 0.6rem;
    background: rgba(12, 12, 20, 0.72);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: rgba(255, 255, 255, 0.5);
    cursor: pointer;
    transition: all 0.18s ease;
    font-size: 0.7rem;
    font-weight: 600;
    font-family: inherit;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  }

  .legend-toggle:hover {
    color: rgba(255, 255, 255, 0.9);
    border-color: rgba(255, 255, 255, 0.2);
  }

  .legend-toggle.is-open {
    color: #00ffcc;
    border-color: rgba(0, 255, 204, 0.3);
    background: rgba(0, 255, 204, 0.08);
  }

  .toggle-label {
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }

  .chevron {
    transition: transform 0.2s ease;
  }

  .chevron.rotated {
    transform: rotate(180deg);
  }

  /* --- Panel --- */
  .legend-panel {
    background: rgba(12, 12, 20, 0.78);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 0.65rem 0.75rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    animation: slideUp 0.2s ease-out;
    min-width: 200px;
    max-width: 260px;
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .legend-title {
    font-size: 0.6rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: rgba(255, 255, 255, 0.3);
    margin: 0 0 0.55rem;
  }

  .legend-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .legend-item {
    display: flex;
    align-items: center;
    gap: 0.55rem;
  }

  .color-swatch {
    width: 14px;
    height: 14px;
    border-radius: 3px;
    flex-shrink: 0;
    border: 1px solid rgba(255, 255, 255, 0.15);
  }

  .item-label {
    font-size: 0.72rem;
    color: rgba(255, 255, 255, 0.75);
    line-height: 1.3;
    display: flex;
    align-items: baseline;
    gap: 0.3rem;
  }

  .item-num {
    font-size: 0.6rem;
    color: rgba(255, 255, 255, 0.3);
    font-weight: 700;
    flex-shrink: 0;
  }

  /* --- Responsive: móvil --- */
  @media (max-width: 480px) {
    .legend-wrapper {
      bottom: 1rem;
      left: 0.5rem;
    }

    .legend-panel {
      max-width: calc(100vw - 5rem); /* No sale de pantalla */
      min-width: 160px;
    }

    .color-swatch {
      width: 12px;
      height: 12px;
    }

    .item-label {
      font-size: 0.67rem;
    }

    .toggle-label {
      display: none; /* Solo icono en móvil muy pequeño */
    }
  }
</style>
