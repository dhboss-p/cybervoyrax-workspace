document.addEventListener("DOMContentLoaded",()=>{
  const profileToggle=document.querySelector("[data-profile-toggle]");
  const profileMenu=document.querySelector("[data-profile-menu]");
  const mobileToggle=document.querySelector("[data-mobile-nav-toggle]");
  const mobileNav=document.querySelector("[data-mobile-nav]");
  const mobileScrim=document.querySelector("[data-mobile-nav-scrim]");
  const searchShell=document.querySelector("[data-search-shell]");
  const searchInput=searchShell?.querySelector("input");
  const closeProfile=()=>{profileMenu?.classList.remove("open");profileToggle?.setAttribute("aria-expanded","false")};
  const closeMobile=()=>{mobileNav?.classList.remove("open");mobileScrim?.classList.remove("open")};
  profileToggle?.addEventListener("click",e=>{e.stopPropagation();const open=!profileMenu?.classList.contains("open");closeMobile();profileMenu?.classList.toggle("open",open);profileToggle.setAttribute("aria-expanded",open?"true":"false")});
  profileMenu?.addEventListener("click",e=>e.stopPropagation());
  mobileToggle?.addEventListener("click",e=>{e.stopPropagation();const open=!mobileNav?.classList.contains("open");closeProfile();mobileNav?.classList.toggle("open",open);mobileScrim?.classList.toggle("open",open)});
  mobileScrim?.addEventListener("click",closeMobile);
  document.addEventListener("click",()=>{closeProfile();closeMobile()});
  document.addEventListener("keydown",e=>{
    if(e.key==="Escape"){closeProfile();closeMobile();searchShell?.classList.remove("expanded");searchInput?.blur()}
    if(e.key==="/"&&!/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName||"")){e.preventDefault();searchShell?.classList.add("expanded");searchInput?.focus()}
  });
  searchInput?.addEventListener("focus",()=>searchShell?.classList.add("expanded"));
  searchInput?.addEventListener("blur",()=>setTimeout(()=>searchShell?.classList.remove("expanded"),100));

  const activateTab=name=>{
    document.querySelectorAll("[data-tab]").forEach(x=>x.classList.toggle("active",x.dataset.tab===name));
    document.querySelectorAll("[data-panel]").forEach(x=>x.classList.toggle("active",x.dataset.panel===name));
  };
  document.querySelectorAll("[data-tab]").forEach(t=>t.addEventListener("click",()=>activateTab(t.dataset.tab)));
  document.querySelectorAll("[data-tab-jump]").forEach(t=>t.addEventListener("click",()=>activateTab(t.dataset.tabJump)));

  document.querySelectorAll(".modern-dropzone").forEach(zone=>{
    ["dragenter","dragover"].forEach(type=>zone.addEventListener(type,e=>{e.preventDefault();zone.classList.add("is-dragover")}));
    ["dragleave","drop"].forEach(type=>zone.addEventListener(type,e=>{e.preventDefault();zone.classList.remove("is-dragover")}));
  });
  document.querySelectorAll("[data-file-input]").forEach(input=>input.addEventListener("change",()=>{const n=document.querySelector("[data-file-name]");if(n&&input.files?.[0])n.textContent=`${input.files[0].name} · ${Math.max(1,Math.round(input.files[0].size/1024))} KB`}));

  // Home recent-work filters.
  document.querySelectorAll("[data-work-filter]").forEach(btn=>btn.addEventListener("click",()=>{
    document.querySelectorAll("[data-work-filter]").forEach(x=>x.classList.toggle("active",x===btn));
    const f=btn.dataset.workFilter;
    document.querySelectorAll("[data-work-type]").forEach(row=>row.hidden=f!=="all"&&!row.dataset.workType.includes(f));
    const visible=[...document.querySelectorAll("[data-work-type]")].some(row=>!row.hidden);
    const end=document.querySelector(".feed-end"); if(end) end.hidden=!visible;
  }));

  // A person row remains clickable, while each project relationship can open its project directly.
  document.querySelectorAll("[data-project-href]").forEach(link=>{
    link.setAttribute("role","link");link.setAttribute("tabindex","0");
    const open=e=>{e.preventDefault();e.stopPropagation();window.location.href=link.dataset.projectHref};
    link.addEventListener("click",open);
    link.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" ") open(e)});
  });

  // Projects list filtering and list/board switch.
  let projectStatus="ALL";
  const projectSearch=document.querySelector("[data-project-search]");
  const applyProjectFilters=()=>{const q=(projectSearch?.value||"").trim().toLowerCase();document.querySelectorAll("[data-project-list] [data-status]").forEach(row=>{row.hidden=(projectStatus!=="ALL"&&row.dataset.status!==projectStatus)||(q&&!row.dataset.name.includes(q))})};
  document.querySelectorAll("[data-project-filter]").forEach(btn=>btn.addEventListener("click",()=>{projectStatus=btn.dataset.projectFilter;document.querySelectorAll("[data-project-filter]").forEach(x=>x.classList.toggle("active",x===btn));applyProjectFilters()}));
  projectSearch?.addEventListener("input",applyProjectFilters);
  document.querySelectorAll("[data-project-view]").forEach(btn=>btn.addEventListener("click",()=>{const board=btn.dataset.projectView==="board";document.querySelector("[data-project-list]")?.toggleAttribute("hidden",board);document.querySelector("[data-project-board]")?.classList.toggle("active",board);document.querySelectorAll("[data-project-view]").forEach(x=>x.classList.toggle("active",x===btn))}));

  // Documents filtering.
  let docMode="all";const docSearch=document.querySelector("[data-document-search]");const mineBtn=document.querySelector('[data-document-filter="mine"]');const currentUser=mineBtn?.dataset.currentUser||"";
  const applyDocs=()=>{const q=(docSearch?.value||"").trim().toLowerCase();document.querySelectorAll("[data-document-list] [data-title]").forEach(row=>{const modeFail=docMode==="mine"&&row.dataset.owner!==currentUser||docMode==="project"&&!row.dataset.project;row.hidden=modeFail||(q&&!row.dataset.title.includes(q))})};
  document.querySelectorAll("[data-document-filter]").forEach(btn=>btn.addEventListener("click",()=>{docMode=btn.dataset.documentFilter;document.querySelectorAll("[data-document-filter]").forEach(x=>x.classList.toggle("active",x===btn));applyDocs()}));docSearch?.addEventListener("input",applyDocs);

  // Admin people filtering.
  let adminFilter="all";const adminSearch=document.querySelector("[data-admin-user-search]");const applyAdmin=()=>{const q=(adminSearch?.value||"").trim().toLowerCase();document.querySelectorAll("[data-admin-user-list] [data-name]").forEach(row=>{const f=adminFilter==="all"?false:adminFilter==="DISABLED"?row.dataset.status!=="DISABLED":row.dataset.role!==adminFilter;row.hidden=f||(q&&!row.dataset.name.includes(q))})};
  document.querySelectorAll("[data-admin-role]").forEach(btn=>btn.addEventListener("click",()=>{adminFilter=btn.dataset.adminRole;document.querySelectorAll("[data-admin-role]").forEach(x=>x.classList.toggle("active",x===btn));applyAdmin()}));adminSearch?.addEventListener("input",applyAdmin);

  // Inbox filters.
  document.querySelectorAll("[data-inbox-filter]").forEach(btn=>btn.addEventListener("click",()=>{const mode=btn.dataset.inboxFilter;document.querySelectorAll("[data-inbox-filter]").forEach(x=>x.classList.toggle("active",x===btn));document.querySelectorAll("[data-inbox-list] [data-read]").forEach(row=>row.hidden=mode==="unread"&&row.dataset.read==="yes")}));
});
