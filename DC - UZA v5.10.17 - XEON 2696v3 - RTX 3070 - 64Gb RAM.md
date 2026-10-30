Ниже — только то, что зафиксировано в логах. Без рекомендаций. По группам.

## 1. Flywheel принудительно уходит с GPU на CPU при активном Oculus
В `latest.log` 8 раз:
- `17:47:34,611` — `Flywheel backend fell back from 'flywheel:instancing' to 'flywheel:off'`
- `17:47:48,769`, `18:24:42,935`, `18:24:42,956`, `19:29:40,766`, `19:29:40,787`, `20:37:09,410`, `20:37:09,427` — то же самое.

Каждое совпадает с `Creating pipeline for dimension ... overworld` / переключением шейдеров. То есть при включённом Oculus рендер Create переходит на CPU-бэкенд.

## 2. Массовые mixin-конфликты Embeddium ↔ Oculus (и другие)
`Embeddium-MixinTaintDetector` явно перечисляет классы рендера, которые модифицирует Oculus:
`SodiumGameOptions`, `SodiumOptionsGUI`, `VertexFormatDescriptionImpl`, `SodiumBufferBuilder`, `SodiumWorldRenderer`, `RenderSectionManager`, `ChunkBuilderMeshingTask`, `ChunkMeshFormats`, `ChunkMeshAttribute`, `GlVertexFormat$Builder`, `GlVertexAttributeFormat`, `DefaultChunkRenderer`, `ShaderChunkRenderer`, `ChunkBuildBuffers`, `ChunkMeshBufferBuilder`, `BakedChunkModelBuilder`, `SmoothLightPipeline`, `FlatLightPipeline`, `GlProgram`, `ShaderType`, `CloudRenderer`, `RenderRegion$DeviceResources`, `BakedModelEncoder`, `VertexSerializerRegistryImpl`, `GLRenderDevice$ImmediateDrawCommandList`.

Плюс другие моды лезут в тот же конвейер чанков:
- `sodiumdynamiclights` → `LightDataAccess`, `ArrayLightDataCache`, `FlatLightPipeline`;
- `entity_texture_features` → `SodiumBufferBuilder`;
- `flerovium` → `OcclusionCuller`;
- `culllessleaves`, `bocchium` → `BlockOcclusionCache`;
- `betterbiomereblend` → `WorldSlice`.

Всё это — путь отрисовки чанков и вершинных буферов.

## 3. Утечка LevelChunk и рост heap
`AllTheLeaks` каждые 5 минут:
- LevelChunk: 92 → 23 → 41 → 135 → 58 → 80 → 120 → 143 → 182 → 356 → 379 → 466 → 483 → 506 → 674 → 697 → 719 → 1002 → 1004 → 1088 → **1173**.
- Heap: `B: 3347MB / C: 4755MB / Diff: +1408MB` в конце.

То есть базовый heap не растёт, но `LevelChunk` копится монотонно и не освобождается. Также в `17:46:31,949` ModernFix: `One or more BufferBuilders have been leaked`.

## 4. Серверный тик-лаг и подготовка spawn region
- `17:47:33,716` `Server thread`: `Can't keep up! Is the server overloaded? Running 2189ms or 43 ticks behind`.
- `17:47:25,364` `LoggerChunkProgressListener`: `Time elapsed: 81343 ms`.
- Спавн игрока: `(-1608.475…, 72.0, 10296.094…)` — далеко от нуля, при спавне грузятся чанки на удалённых координатах.

## 5. Shader uniform mismatch
Шейдеры модов запускаются в пайплайне Oculus, но не находят униформы/сэмплеры:
- `moreplayermodels:position_tex_normal` → нет `FogStart`, `FogEnd`, `FogColor`;
- `clouds` → нет `ModelViewMat`, `ProjMat`, `ColorModulator`, `FogStart`, `FogEnd`, `FogColor`;
- `rendertype_entity_translucent_emissive` → нет `Sampler2`;
- `watut:position_tex_blur`, `..._blur_horizontal`, `..._blur_vertical` → нет `ColorModulator`;
- `moonlight:text_alpha_color` → нет `Sampler2`, `IViewRotMat`.

## 6. ModelMissingException — повторные попытки печь модели
`Chunk Render Task Executor` и `Render thread` постоянно:
`Unable to load model: 'minecraft:corpse' / 'barricadec' / 'marketfridge' / 'iron_shelf_vazia' / 'iron_shelf' / 'largeshelvese' / 'marketempty' / 'tv' / 'largeshelves' / 'iron_shelf_dois' / 'market' / 'ironlocker' / 'radioold' / 'iron_shelf_tres' / 'ironsafe' / 'iron_shelf_quatro' / 'plasmatv' / 'medical_i' / 'barricade' / 'trash_can_2' / 'trash_bag' / 'reta' / 'placa' / 'sera' / 'katana' / 'lancafaca' / 'padeneve' / 'garfo' / 'lancademadeira' / 'lanca' / 'katanafire' / 'glove' / 'glove_t' / 'flamethrower' / refinedstorage:cover#inventory`.
Все — из `apocalypsenow` и `refinedstorage`. Каждое сопровождается `ModelMissingException`, в том числе **в потоках рендера чанков**, то есть при отрисовке.

Плюс на старте — серия `Exception baking storagedrawers:...` для `meta_framed_drawers_*`, `meta_framed_compdrawers_2_*`, `compacting_drawers_2`, `framed_compacting_drawers_2` и др.

## 7. Стоимость старта
- `ModernFix`: `Game took 97.038 seconds to start`; `Total time to load game and open world was 127.681335 seconds`.
- `Initial datapack load took 14.46 s`.
- `Early baking 914 models`.
- `Posting dynamic ModelEvent.ModifyBakingResult ... took 2.230 s` — разбивка: `create 814.0 ms`, `modernfix 500.1 ms`, `chalk 344.7 ms`, `storagedrawers 176.2 ms`, `cfm 152.6 ms`, `bigreactors 105.0 ms`, `securitycraft 101.0 ms`.
- `Starting JEI took 12.01 s`; `Registering Runtime took 5.031 s`; `Adding 14379 ingredients` — `4.627 s`.
- `Loaded 111 shader sources in 51.151 ms` (Flywheel; в русской локали запятая = десятичный разделитель).
- `Loaded 360 mods`, `Found 91 dependencies`.

## 8. Шторм перезагрузок advancement
`Loaded … advancements` повторяется ~25 раз: `11424 → 1768 → 1829 → 1851 → 1854 → 1855 → 1875 → 1883 → 1886 → 1908 → 1909 → 1910 → 1911 → 1912 → 1913 → 1918 → 1919 → 1923 → 1924 → 1927 → 1928 → 1946 → 1949 → 1969 → 1971`. Каждый раз — перестройка дерева достижений на клиенте.

## 9. Refmap read failures
Не читаются refmap у: `parcool_compat_addon`, `jsconf`, `LongerChatHistory`, `fastpaintings`, `colorwheel_patcher`, `cobweb` (×2 конфига), `item_scrapper`, `dsp`, `lmft`, `harvest_with_ease` (×2), `clickmachine`, `puzzlesaccessapi`, `v_slab_compat`, `mcreator_mem_fix`, `trashslot`, `coroutil`, `adapter.init.mixins.json`. Лог сам пишет: `Find from all resources will spend extra time`.

## 10. Пропущенные оптимизации из-за конфликтов
Явные `@Redirect conflict` / `Method overwrite conflict` — оптимизация одного мода не применилась:
- `redirected` (PistonBaseBlock, RedStoneWireBlock, PistonStructureResolver) ↔ `radium`;
- `packetfixer` (ClientboundCustomPayloadPacket, ServerGamePacketListenerImpl, ServerLoginPacketListenerImpl) ↔ `connectivity`;
- `recipeessentials` RecipeManager ↔ `modernfix`;
- `embeddium` Frustum ↔ `flerovium` FrustumMixin;
- `lithium` SortedArraySetMixin ↔ `modernfix` SortedArraySetMixin;
- `redirected` CacheMixin ↔ `modernfix` AbstractBlockStateCacheMixin;
- `lithium` BiomeMixin `m_47505_` ↔ `modernfix` remove_biome_temperature_cache.

## 11. ConcurrentModificationException во время трансформации классов
`17:45:53,020` в `Thread-22` (stderr, и в `latest.log` стек):
`java.util.ConcurrentModificationException` в `cpw.mods.modlauncher.LaunchPluginHandler.computeLaunchPluginTransformerSet` → вызывается из `modernfix … NightConfigWatchThrottler$1.values()`. Происходит в момент, когда загрузчик классов трансформирует классы.

## 12. ModernFix отключён частично
`settingdust.lazyyyyy.LazyyyyyMixinCanceller`: `Disabled ModernFix perf.dynamic_entity_renderers`, `Cancelled mixin org.embeddedt.modernfix.common.mixin.perf.dynamic_entity_renderers.EntityRenderDispatcherMixin`. Плюс из конфига ModernFix: `mixin.perf.thread_priorities` переопределён на `false` модом `smoothboot`.

## 13. SodiumDynamicLights частично несовместим с Embeddium
`Error loading class: net/caffeinemc/mods/sodium/client/model/light/data/LightDataAccess` (×2), `ArrayLightDataCache` (×2), `FlatLightPipeline` (×2) — `ClassNotFoundException`. При этом ниже идёт `Embeddium-MixinTaintDetector`: `Mod(s) [sodiumdynamiclights] are modifying Embeddium class me.jellysquid...LightDataAccess / ArrayLightDataCache`, то есть мод таргетит пакет Sodium, а установлен Embeddium.

## 14. Oculus не парсит block ID map
`17:47:01,255` / `17:47:01,299` и повтор на каждой смене шейдеров: `Error while parsing the block ID map entry for "block.10021"` и `"block.10005"`.

## 15. Постоянное пересоздание GPU pipeline
`Oculus: Creating pipeline for dimension …` / `Destroying pipeline …` — на старте, при переключении шейдеров вкл/выкл, при смене измерения, при перезагрузке ресурсов. Каждый раз — `ChunkBuilder: Stopping worker threads` → `Started 16 worker threads`.

## 16. VRAM-атласы
- `Created: 4096x4096x4 minecraft:textures/atlas/blocks.png-atlas` — 4K×4K блоков.
- `particles.png-atlas` 2048×2048; `armor_trims` 2048×1024; `chest` 1024×1024.
- `Texture undead_revamp2:item/sugarcoat with size 491x431 limits mip level from 1 to 0` — очень большая текстура в атласе.
- `texture displaydelight:block/cd_cornbread_stuffing with size 8x8 limits mip level from 4 to 3`.

## 17. Сетевые таймауты в фоновых потоках
- Xaero: `io exception while checking patreon: Read timed out`, `io exception while checking versions: Read timed out`, `Online mod data expired! Date: Wed Oct 28 17:27:27 MSK 2026`.
- `CorgiLib: GET request failed. Response Code: 301`.
- CraftPresence: `atlauncher pack data`, `curse pack data`, `GET`-ошибки, `Значок с именем "deceasedcraft-urbanzombieapocalypse" не существует`.

## 18. KubeJS: ошибки рецептов
`Your custom create:compacting recipe (deceasedcraft:compacting/seed_oil) has more item inputs (10) than supported (9)`.

## 19. Hordes: отсутствующая таблица и повторные события
- `Failed loading table hordes:mobs_normal_10, loading fallback table hordes:fallback` — таблицы на день 10 нет, используется `fallback` (только `minecraft:zombie`, weight 30).
- `Trying to start horde event on day 15 with nextDay 15 and time 13000` повторяется в `18:34:46`, `18:51:08`, `18:52:48`, `18:54:28`, `18:56:08`. На каждую волну — по 20+ пар строк `Applying script hordes:wave_0/1_normal_loot_script`.

## 20. Spore: перебор всех типов сущностей
Длинный список `Could not apply custom armor to entity type ...: class ... cannot be cast to class ...LivingEntityRenderer` — от `minecraft:area_effect_cloud` до `tacz:target_minecart`, `create:*`, `undead_revamp2:*`, `zombie_extreme:*`, `naturalist:*`, `spore:*`. Это проход по реестру сущностей при инициализации рендера.

## 21. EMF: переопределение PlayerModel
`Entity model [net.minecraft.client.model.PlayerModel] has been overridden by [noppes.npcs.client.renderer.RenderCustomNpc$2] likely from a mod.`

## 22. FancyMenu: перехват каждого экрана
`ScreenCustomizationLayer registered:` — на `pause_screen`, `inventory_screen`, `container_screen`, `crafting_screen`, `options_screen`, `controls_screen`, `RecipesGui` (JEI), `ScreenWrapper` (FTB), `DietScreen`, `BackpackScreen`, `CuriosScreenV2`, `GunSmithTableScreen` (TACZ), `PonderUI`, `SkillsScreen` (Puffish), `SignEditScreen`, `LoomScreen`, экраны ParCool, Apocalypse Now, CustomNPC и т.д.

## 23. «defineId called for»
`SynchedEntityData`: `defineId called for: class ...Busser from class ...Scamper / Vigil / Brauerei / Hyper` (Spore) и `class net.minecraft.world.entity.player.Player from class tschipp.carryon.common.cache.CarryOnDataManager`.

## 24. Audio device lost
`19:26:43,301` `Audio device was lost!` → `OpenAL initialized` → повторная инициализация `Sound Physics`. До этого — пачка `Missing sound for event: minecraft:item.goat_horn.play`, `naturalist:tortoise_hurt/death`, `sounds:item.hard_metal.hold`, `sounds:item.shiny_metal.hold`.

## 25. «Narrow places» по железу из самого лога
- CPU (Oculus hardware info): `16x Intel(R) Xeon(R) CPU E5-2696 v3 @ 2.30GHz` — базовая частота 2.3 ГГц, Haswell-EP. Игровой поток MC и главный поток рендера упираются в однопоточную производительность этого ядра, а не в 3070.
- GPU: `NVIDIA GeForce RTX 3070/PCIe/SSE2 (OpenGL 3.2.0 NVIDIA 621.01)`, драйвер `32.0.16.2101`.
- Embeddium применил `workarounds [NVIDIA_THREADED_OPTIMIZATIONS]` и `Applying workaround: Prevent the NVIDIA OpenGL driver from using broken optimizations (NVIDIA_THREADED_OPTIMIZATIONS)` — то есть часть драйверных оптимизаций NVIDIA отключена самим Embeddium.
- `Changing simulation distance to 5, from 0` — сервер выставил simulation distance = 5.
- `ChunkBuilder: Started 16 worker threads` — 16 потоков под рендер чанков.

Резюме по логам, без оценок и предложений: в логах одновременно присутствуют (а) принудительный откат Flywheel на CPU-бэкенд при Oculus, (б) массовая модификация Oculus/другими модами классов рендера чанков Embeddium, (в) монотонная утечка `LevelChunk` с ростом heap до +1.4 ГБ, (г) `Can't keep up! … 43 ticks behind` на серверном потоке, (д) постоянные `ModelMissingException` для `apocalypsenow`/`refinedstorage`/`storagedrawers`, (е) шейдерные униформы модов не находятся в пайплайне Oculus, (ж) пропуск части оптимизаций из-за `@Redirect`/`Method overwrite` конфликтов, (з) отключение части ModernFix через lazyyyyy, (и) фоновая нагрузка от сетевых таймаутов и повторных sync advancement, (к) CPU с базовой частотой 2.3 ГГц как однопоточное ограничение.
