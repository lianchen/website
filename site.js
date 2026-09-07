(() => {
  const viewLinks = [...document.querySelectorAll('[data-view]')];
  function updateCurrentView() {
    const currentView = ['#teaching', '#teaching-main'].includes(location.hash) ? 'teaching' : 'research';
    viewLinks.forEach(link => {
      if (link.dataset.view === currentView) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
  }
  window.addEventListener('hashchange', updateCurrentView);
  updateCurrentView();

  const filterPanel = document.querySelector('.topic-filters');
  const buttons = [...document.querySelectorAll('[data-filter]')];
  const publicationPanel = document.querySelector('.publication-filters');
  const publicationButtons = [...document.querySelectorAll('[data-publication-filter]')];
  const papers = [...document.querySelectorAll('.paper')];
  const groups = [...document.querySelectorAll('.paper-group')];
  const jumpLinks = [...document.querySelectorAll('.jump-item')];
  const jumpNav = document.querySelector('.jump-links');
  const status = document.getElementById('filter-status');
  if (!filterPanel || !status || !buttons.length) return;

  filterPanel.hidden = false;
  if (publicationPanel) publicationPanel.hidden = false;
  let selectedTopic = 'all';
  let selectedPublicationType = 'all';

  const matchesTopic = paper => selectedTopic === 'all' || paper.dataset.topics.split(' ').includes(selectedTopic);

  function applyFilters() {
    if (publicationPanel) publicationPanel.hidden = selectedTopic !== 'all';
    if (selectedTopic !== 'all') selectedPublicationType = 'all';
    const publicationsForTopic = papers.filter(paper => paper.dataset.publicationType && matchesTopic(paper));
    publicationButtons.forEach(button => {
      const type = button.dataset.publicationFilter;
      button.disabled = type !== 'all' && !publicationsForTopic.some(paper => paper.dataset.publicationType === type);
    });
    if (selectedPublicationType !== 'all' && !publicationsForTopic.some(paper => paper.dataset.publicationType === selectedPublicationType)) {
      selectedPublicationType = 'all';
    }
    papers.forEach(paper => {
      const matchesType = !paper.dataset.publicationType || selectedPublicationType === 'all' || paper.dataset.publicationType === selectedPublicationType;
      paper.hidden = !(matchesTopic(paper) && matchesType);
    });
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === selectedTopic)));
    publicationButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.publicationFilter === selectedPublicationType)));
    groups.forEach(group => {
      const hasMatches = [...group.querySelectorAll('.paper')].some(paper => !paper.hidden);
      group.hidden = !hasMatches;
    });
    jumpLinks.forEach(item => {
      const target = document.getElementById(item.querySelector('a').hash.slice(1));
      item.hidden = target.hidden;
    });
    if (jumpNav) jumpNav.hidden = jumpLinks.every(item => item.hidden);
    const topicLabel = buttons.find(button => button.dataset.filter === selectedTopic).textContent.trim();
    const typeLabel = publicationButtons.find(button => button.dataset.publicationFilter === selectedPublicationType)?.textContent.trim() || 'All';
    status.textContent = selectedTopic === 'all' && selectedPublicationType === 'all'
      ? 'All papers displayed.'
      : `${topicLabel} topics. Publications: ${typeLabel}.`;
  }

  buttons.forEach(button => button.addEventListener('click', () => {
    selectedTopic = button.dataset.filter;
    applyFilters();
  }));
  publicationButtons.forEach(button => button.addEventListener('click', () => {
    selectedPublicationType = button.dataset.publicationFilter;
    applyFilters();
  }));
  applyFilters();
})();
