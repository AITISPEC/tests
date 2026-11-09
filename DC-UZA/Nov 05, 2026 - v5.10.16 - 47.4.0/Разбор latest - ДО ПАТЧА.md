## Пять часов игры со стримом на Твитч: высотки, орды зомби.

*Пять списков логов:*
 - «Зелёные» — работают и показывают результат
 - «Жёлтые» — работают, но тянут одеяло / конфликтуют «по-тихому»
 - «Красные» — перебои, конфликты, битые ассеты, ошибки
 - «Чёрные» — кандидаты в мёртвый груз
 - «Фиолетовые» — «зомби»: работают, но несут в основном отрицательную нагрузку

## 1. «Зелёные» — работают и показывают результат

Опираюсь на конкретные строки, а не на общий список модов.

- **ModernFix** — `Bypassed Mojang DFU`, `Applied Forge config corruption patch`, `Injecting BlockStateBase cache population hook`, `Made Refined Storage shape cache map thread-safe`. Плюс `Game took 95.092 seconds to start` и `Total time to load game and open world was 125.585` — для 360 модов это хороший показатель. Делает много, ошибок не даёт.
- **Embeddium** — `Found graphics card: ... RTX 3070`, `Applying workaround: Prevent the NVIDIA OpenGL driver from using broken optimizations`, корректно обрабатывает color providers (`had its color provider replaced`). Работает стабильно.
- **Packet Fixer** — `Packet Fixer forge 1.19.4-1.20.1 has been applied successfully.` Без оговорок.
- **KubeJS** — `Loaded 30/30 KubeJS startup scripts in 1.698 s with 0 errors and 0 warnings` и `Loaded 1/1 KubeJS client scripts ... 0 errors and 0 warnings`. Чистый результат.
- **ImmediatelyFast** — `Initializing ImmediatelyFast ... on NVIDIA GeForce RTX 3070`, `Found Iris/Oculus 1.8.0. Enabling compatibility.` Без ошибок.
- **Entity Texture Features** — `[ETF]: emissive suffixes loaded: {_e}.`, `6 new ETF Random Properties registered by entity_model_features.` Работает.
- **Simple Voice Chat** — `Successfully authenticated player`, `Player Nechosi ... successfully connected to voice chat`, `Loaded 2 plugin(s)`. Полный цикл.
- **Xaero's Minimap / WorldMap** — `World Map found!`, `Iris found!`, `Successfully reloaded the minimap shaders!`. Без конфликтов.
- **Oculus (как загрузчик шейдеров)** — несмотря на предупреждения (см. жёлтые), пайплайн создаётся: `Creating pipeline for dimension ... overworld`, `Using shaderpack: ComplementaryUnbound_r5.6.1 + Clrwl_1.0.3.zip`. Шейдеры реально включились (`Включён набор шейдеров`).
- **Create** — `Create 6.0.6 initializing!`, `Created 472 recipes which will be injected`, `Loaded 56 train hat configurations.` Без ошибок.
- **FTB Quests** — `Loaded 8 chapter groups, 30 chapters, 801 quests, 1 reward tables`. Чисто.
- **Curios** — `Loaded 14 curio slots`, `Loaded 11 curio entities`, `initialized with 18 slot(s) after 0 tries`. Работает.

---

## 2. «Жёлтые» — работают, но тянут одеяло / конфликтуют «по-тихому»

- **JEI** — `Starting JEI took 12.90 s`, `Registering Runtime: jei:forge_gui took 5.440 seconds`, `Building ingredient filter took 4.898 s`, `jei:forge_gui is running and has taken 5.047 seconds so far`. Также `Recipe registry plugin is slow, took 13.02 ms`. Работает, но это ощутимый кусок времени загрузки.
- **FancyMenu** — регистрирует `ScreenCustomizationLayer` почти для каждого экрана, `Reloading AudioResourceHandler after Minecraft SoundEngine reload`, `Pre-loading resources`, и при этом `Failed to read texture ... accessibility.png`. Работает, но лезет во всё и спамит.
- **Oculus (как патчер)** — при каждом создании пайплайна: `Failed to resolve uniform inPaleGarden, reason: Unknown variable: BIOME_PALE_GARDEN` (полный стектрейс ×3 раза за сессию), `Error while parsing the block ID map entry for "block.10104"`. Шейдеры работают, но предупреждения постоянные.
- **Flywheel** — `Flywheel backend fell back from 'flywheel:instancing' to 'flywheel:off'` повторяется много раз (создание мира, смена шейдеров, релоады). Работает, но в деградированном режиме.
- **Flerovium** — `Method overwrite conflict for sodium$createViewport in embeddium.mixins.json ... previously written by com.moepus.flerovium.mixins.Chunk.FrustumMixin. Skipping method.` Плюс он модифицирует Embeddium (`Embeddium-MixinTaintDetector`). Работает, но трётся с Embeddium.
- **Connectivity ↔ Packet Fixer** — взаимные пропуски: `@ModifyConstant conflict. Skipping connectivity ... already redirected by packetfixer` и обратное `@ModifyConstant conflict. Skipping packetfixer ... already redirected by connectivity`. Один из них на каждом таргете оказывается «проигравшим». Работают частично.
- **Radium ↔ Redirected ↔ ModernFix** — `@Redirect conflict. Skipping mixins.redirected_forge_1.20.1.json ... already redirected by lithium ... from mod radium`, `Method overwrite conflict for m_47505_ ... previously written by modernfix`. Все трое живы, но перекрывают друг друга, и `redirected` в этих точках просто выключен.
- **RecipeEssentials** — `@Redirect conflict. Skipping recipeessentials.mixins.json:RecipeManagerMixin ... already redirected by modernfix`. Его конкретный redirect не применяется.
- **Sound Physics Remastered** — десятки строк `Unknown sound in allowed sound config: alexsmobs:...` / `naturalist:...` / `car:...`. EFX при этом `ready`. Работает, но конфиг напичкан несуществующими событиями.
- **Lazyyyyy (settingdust)** — множество `Failed to read refmap ... from ...jar for config ...` по разным модам (`parcool_compat_addon`, `jsconf`, `LongerChatHistory`, `fastpaintings`, `colorwheel_patcher`, `cobweb`, `item_scrapper`, `dsp`, `lmft`, `harvest_with_ease`, `clickmachine`, `puzzlesaccessapi`, `v_slab_compat`, `trashslot`, `coroutil`). Сам мод работает (он же `Disabled ... due to config` для дорогих миксинов — это полезно), но шума много.
- **CraftPresence** — `Unable to get "atlauncher" pack data`, `Значок с именем "deceasedcraft-urbanzombieapocalypse" не существует`, `Значок с именем "overworld" не существует`, `Попытка подключения к Discord (1/10)`. Работает, но постоянно ошибки иконок.

---

## 3. «Красные» — перебои, конфликты, битые ассеты, ошибки

- **Apocalypse Now** — десятки `Unable to load model: 'minecraft:...' referenced from: apocalypsenow:...` (`largeshelvese`, `iron_shelf`, `ironsafe`, `ironlocker`, `plasmatv`, `radioold`, `medical_i`, `barricadec`, `tv`, `corpse`, `milisto`, `marketfridge`, `marketempty`, `market`, `trash_bag`, `trash_can_1/2`, `sodamachine`, `sodamachineblue`, `pneu`, `gascanister`, `glove`, `glove_t`, `glove_b`, `brassk`, `katana`, `lanca`, `garfo`, `reta`, `placa`, `sera`, `padeneve` и др.). Мод грузится, но уйма моделей отсутствует — визуально это битые текстуры/плейсхолдеры.
- **Storage Drawers** — `Exception loading blockstate definition: 'storagedrawers:blockstates/meta_framed_drawers_shading.json' missing model for variant...` (десятки вариантов), `Exception baking storagedrawers:compacting_drawers_2#...: org.embeddedt.modernfix.dynamicresources.ModelMissingException`. Ломается на этапе бейка моделей.
- **TACZ (gun pack bf1)** — `bf1:rsc1917_display display init read fail! java.lang.IllegalArgumentException: there is no corresponding model file`. Битый gun pack.
- **AllTheLeaks** — `Cannot have null removal reason on Clone event!` (несколько раз при смертях/респавнах), `Method handleAnimations at mixin ... cancelled due to not matching hash`, `Mixin annotation ... removed due to no methods available`, `Modified mixin ...`. Сам мод заявляет об утечках, но и сам же регулярно отменяет/удаляет свои миксины из-за несовпадения хэшей.
- **Advancement-парсинг** — `Parsing error loading custom advancement animal_pen:grant_book_on_first_join: Advancement criteria cannot be empty`, `Parsing error loading custom advancement parcool:grant_parcool_guide: Advancement criteria cannot be empty`. Два адвансмента с пустыми критериями.
- **POI** — `POI data mismatch: never registered at BlockPos{x=..., y=..., z=...}` (несколько раз: `-3209,65,8001`, `-3378,65,8007`, `-3298,65,8183`, `-3314,65,7959`, `-3306,96,8188`, `-1605,76,10291`, `-1606,76,10291`). Данные точек интереса не сходятся.
- **ConcurrentModificationException** — `[Thread-22/INFO] [STDERR]: java.util.ConcurrentModificationException` в `LaunchPluginHandler.computeLaunchPluginTransformerSet` / `FileWatcher$WatcherThread`. Реальное исключение на старте.
- **Refined Storage** — `Unable to load model: 'refinedstorage:cover#inventory' ... FileNotFoundException: refinedstorage:models/item/cover.json` + `Exception baking refinedstorage:cover#inventory: ModelMissingException`.
- **«Can't keep up»** — `Can't keep up! Is the server overloaded? Running 2190ms or 43 ticks behind` (и ещё несколько: 2240ms/44, 2150ms/43, 2105ms/42, 2041ms/40, 2113ms/42). Серверная часть отстаёт во время орд.
- **Embeddium tainted** — `Mod mixin into Embeddium internals detected. This instance is now tainted.` Список модов, которые лезут в Embeddium: `oculus`, `sodiumdynamiclights`, `entity_texture_features`, `betterbiomereblend`, `culllessleaves`, `bocchium`, `flerovium`. Сам Embeddium предупреждает, что гарантий поддержки нет.
- **Sodium-классы не найдены** — `Error loading class: net/caffeinemc/mods/sodium/client/model/light/data/ArrayLightDataCache`, `...FlatLightPipeline`, `...LightDataAccess` (несколько раз). Это Oculus/SodiumDynamicLights/BetterBiomeBlend пытаются патчить Sodium, которого нет (стоит Embeddium). Миксины не применяются.
- **Mixin target not found** (опциональные compat-миксины, но факт есть факт): `securitycraft` → `betterf3.TargetModule`; `create_hypertube` → `betterthirdperson.CustomCamera`/`CustomCameraManager`; `create_radar` → `cbcat...MountedTwinAutocannonContraption`/`MountedHeavyAutocannonContraption`; `rsmixin` → куча `cabletiers.*`, `enderio.*`, `extrastorage.*`, `rebornstorage.*`, `refinedcrafterproxy.*`, `refinedstoragerequestify.*`; `particular` → `tfc.MixingFluid`/`RiverWaterFluid`; `stylisheffects` → `jei.InventoryEffectRendererGuiHandler`; `createbigcannons` → `framedblocks.FramedAdjustableDoubleBlockEntity`; `deceased_expansion` → `lcmultithreaded.PlayerPreloader`; `lazyyyyy` → `jitl.ClientLoginChecker`, `cabletiers.ClientEventHandler`, `simplyswords.Config`, `structurify.ImageButtonWidget`; `create` → `journeymap.Fullscreen`. Много «мёртвых» целей.
- **CorgiLib** — `GET request failed. Response Code: 301`. Мелочь, но ошибка.
- **ytongame_hostingmenu** — `Failed to load hosting packages from remote: Connect timed out` → fallback на локальные 5 пакетов.
- **EMF ↔ customnpcs** — `Entity model [net.minecraft.client.model.PlayerModel] has been overridden by [noppes.npcs.client.renderer.RenderCustomNpc$2] likely from a mod.` Перехват модели игрока.
- **`Received passengers for unknown entity`** — повторяется несколько раз. Клиент получает пассажиров неизвестной сущности.
- **Shader uniforms not found** — `moreplayermodels:position_tex_normal could not find uniform named FogStart/FogEnd/FogColor`, `watut:position_tex_blur... ColorModulator`, `moonlight:text_alpha_color sampler Sampler2/IViewRotMat`, `clouds ... ModelViewMat/ProjMat/ColorModulator/FogStart/FogEnd/FogColor`, `rendertype_entity_translucent_emissive sampler Sampler2`. Не крашит, но шейдеры недополучают униформы — это не «зелёное».

---

## 4. «Чёрные» — кандидаты в мёртвый груз

Здесь я обязан оговориться: **отсутствие строк в логе ≠ мод мёртв**. Многие тихие оптимизаторы просто не пишут в лог. Поэтому список ниже — это «кандидаты, по которым в этом логе нет признаков реальной работы», а не приговор.

- **`redirected`** — все его `@Redirect` в логе пропущены (`Skipping mixins.redirected_forge_1.20.1.json ... already redirected by lithium ... from mod radium`) на `PistonBaseBlock`, `RedStoneWireBlock`, `PistonStructureResolver`, `CacheMixin`. В этих точках он не работает.
- **`connectivity`** (частично) — его `@ModifyConstant` на таймауты пропущен из-за `packetfixer` и наоборот. Часть функций не применяется.
- **`recipeessentials`** (частично) — `@Redirect logErrorOnce` пропущен из-за `modernfix`. Конкретно этот патч не работает.
- **`fastboot` / `fastload` / `gpu_tape` / `mobtimizations` / `toofast`** — присутствуют в списке 360 модов, но в логе **ни одной** строки активности. Либо работают молча, либо не задействованы. Проверить по логу нельзя.
- **`Better Compatibility Checker`** — только `starting` и `setup`; никакого видимого результата в логе.
- **`smoothboot`** — единственное упоминание: `Option 'mixin.perf.thread_priorities' overriden (by mods [smoothboot]) to 'false'`. То есть он отключает оптимизацию ModernFix, а своих следов не оставляет.

Это самые честные кандидаты. Всё остальное из списка 360 модов я не берусь называть мёртвым без прямых доказательств.

---

## 5. «Фиолетовые» — «зомби»: работают, но несут в основном отрицательную нагрузку

- **AllTheLeaks** — самый яркий кандидат. Он *заявляет* о поимке утечек, но по логу: (а) `Cannot have null removal reason on Clone event!` — его собственные ошибки; (б) его отчёты показывают рост `Diff: +708MB → +3363MB` за 5 часов; (в) он держит и пересчитывает `LevelChunk` тысячами (`424 → 438 → 1599 → 2858 → 4796 → 7887`), (г) его собственные миксины регулярно `cancelled due to not matching hash` / `removed due to no methods available`. То есть он и «лечит», и сам создаёт заметную нагрузку и шум.
- **CraftPresence** — Discord-статус. Работает, но в логе: `Unable to get "atlauncher" pack data`, две ошибки иконок, `Попытка подключения к Discord (1/10)`. Полезной игровой функции не несёт, ошибок даёт.
- **`moe.ytonidc.ytongame_hostingmenu`** — `Failed to load hosting packages from remote: Connect timed out` → `Loaded 5 hosting packages from resources`. Работает на локальном фолбэке, удалённый источник мёртв. Для стрима — просто меню.
- **`CorgiLib`** — `GET request failed. Response Code: 301`. Библиотека, в логе только ошибка запроса.
- **`EMF` в связке с `customnpcs`** — `Entity model [PlayerModel] has been overridden by [noppes.npcs...]`. EMF работает, но на модели игрока его перекрывает CustomNPCs — то есть в этой точке EMF фактически не при деле.
- **Sound Physics Remastered** — спорный кандидат: EFX реально `ready`, но конфиг забит десятками `Unknown sound in allowed sound config`. Если хочешь — могу перенести его в жёлтые; формально он делает работу, но шума от него больше, чем пользы в этом логе.

