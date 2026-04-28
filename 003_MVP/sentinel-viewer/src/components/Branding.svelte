<script lang="ts">
  // En Svelte 4, la reactividad es automática con 'let'
  let isOpen = false;

  const team = [
    { 
      name: "Ivan Pantaleoni", 
      url: "https://www.linkedin.com/in/ivan-pcm/" 
    },
    { 
      name: "Ameneh Alcalá", 
      url: "https://www.linkedin.com/in/ameneh-alcala/?skipRedirect=true" 
    },
    { 
      name: "Antonio López García", 
      url: "https://www.linkedin.com/in/tonilogar/" 
    }
  ];

  const repoUrl = "https://github.com/tonilogardev/cassini_hackathon_barcelona";

  function togglePanel() {
    isOpen = !isOpen;
  }
</script>

<div class="branding-wrapper {isOpen ? 'is-open' : ''}">
  <button 
    class="fab" 
    on:click={togglePanel}
    aria-label={isOpen ? "Cerrar información" : "Ver información del proyecto"}
  >
    {#if !isOpen}
      <span class="icon">🛰️</span>
    {:else}
      <span class="icon">✕</span>
    {/if}
  </button>

  {#if isOpen}
    <div class="glass-panel">
      <div class="header-row">
        <div class="title-group">
          <h1>CASSINI <span>hackathon</span></h1>
          <p class="tagline">Blue Pixel</p>
        </div>
        <a href={repoUrl} target="_blank" rel="noopener noreferrer" class="repo-link" title="Ver GitHub">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path><path d="M9 18c-4.51 2-5-2-7-2"></path></svg>
        </a>
      </div>

      <div class="divider"></div>

      <div class="team-list">
        <span class="section-label">Team Members</span>
        {#each team as member}
          <a 
            href={member.url} 
            target="_blank" 
            rel="noopener noreferrer" 
            class="member-link"
          >
            {member.name}
            <svg class="external-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
          </a>
        {/each}
      </div>
    </div>
  {/if}
</div>

<style>
  .branding-wrapper {
    position: absolute;
    top: 20px;
    left: 20px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    gap: 12px;
    pointer-events: none;
  }

  .branding-wrapper.is-open {
    pointer-events: auto;
  }

  .fab {
    pointer-events: auto;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: rgba(10, 10, 11, 0.9);
    border: 1px solid #00ffcc;
    color: #00ffcc;
    cursor: pointer;
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    font-size: 1.2rem;
    padding: 0;
  }

  .fab:hover {
    transform: scale(1.1);
    background: #00ffcc;
    color: #0a0a0b;
  }

  .glass-panel {
    background: rgba(10, 10, 11, 0.8);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    color: white;
    font-family: 'Inter', system-ui, sans-serif;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7);
    width: 280px;
    animation: slideUp 0.4s ease-out;
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  h1 { margin: 0; font-size: 1.2rem; color: #00ffcc; }
  h1 span { display: block; color: rgba(255, 255, 255, 0.4); font-size: 0.7rem; text-transform: uppercase; }
  .tagline { font-size: 0.75rem; color: rgba(255, 255, 255, 0.6); margin-top: 4px; }
  .divider { height: 1px; background: rgba(255, 255, 255, 0.1); margin: 1.25rem 0; }
  .section-label { display: block; font-size: 0.65rem; text-transform: uppercase; color: rgba(255, 255, 255, 0.3); margin-bottom: 10px; }
  .team-list { display: flex; flex-direction: column; gap: 8px; }
  .member-link { display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; background: rgba(255, 255, 255, 0.03); padding: 10px 12px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.08); color: white; text-decoration: none; transition: all 0.2s; }
  .member-link:hover { background: rgba(0, 255, 204, 0.1); border-color: #00ffcc; color: #00ffcc; transform: translateX(4px); }
  .external-icon { opacity: 0.3; }
  .repo-link { color: rgba(255, 255, 255, 0.3); }
  .repo-link:hover { color: #3498db; }
</style>