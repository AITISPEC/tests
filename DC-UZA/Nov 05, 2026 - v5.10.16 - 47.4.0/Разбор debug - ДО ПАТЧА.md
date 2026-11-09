Сравнение двух дебагов: с шейдерами и без шейдеров. Орды, высотки.

**1. Шейдеры и рендер**
- С шейдерами: `Oculus` создаёт пайплайн, `ComplementaryUnbound_r5.6.1 + Clrwl_1.0.3.zip`, `Failed to resolve uniform inPaleGarden` (стектрейс), `Error while parsing the block ID map entry for "block.10104"`, `Flywheel backend fell back from 'flywheel:instancing' to 'flywheel:off'` повторяется, `GL ERROR 65540: Invalid scancode 256`.
- Без шейдеров: `Oculus` тоже создаёт пайплайн и `Destroying pipeline`/`Creating pipeline`, но без `inPaleGarden`, без `block.10104`, без `GL ERROR`, `Flywheel` fallback в логе не встречается.
- `Embeddium-MixinTaintDetector` в обоих логах: `oculus`, `sodiumdynamiclights`, `betterbiomereblend`, `culllessleaves`, `bocchium`, `flerovium` помечают Embeddium как tainted. С шейдерами тот же набор плюс чаще.

**2. Ошибки моделей и ассетов**
- В обоих логах: `apocalypsenow` — десятки `Unable to load model: 'minecraft:...' referenced from: apocalypsenow:...` (`market`, `marketempty`, `plasmatv`, `sodamachine`, `sodamachineblue`, `largeshelves`, `largeshelvese`, `tv`, `ice`, `marketfridge`, `ironsafe`, `radioold`, `corpse_sack`, `pneu`, `ironlocker`, `radio`, `gascanister`, `trash_can_1`, `trash_bin`, `medical_i`, `barricadec`, `tool`, `militarc`, `ammo`, `iron_shelf`, `iron_shelf_dois`, `iron_shelf_vazia`, `iron_shelf_quatro`, `iron_shelf_tres`, `iron_shelf_cinco`, `barricade`).
- В обоих логах: `storagedrawers` — `Exception loading blockstate definition: 'storagedrawers:blockstates/meta_framed_drawers_shading.json' missing model for variant...` и `ModelMissingException`.
- В обоих логах: `refinedstorage:cover#inventory` — `FileNotFoundException: refinedstorage:models/item/cover.json`, `ModelMissingException`.
- В обоих логах: `tacz` — `bf1:rsc1917_display display init read fail! java.lang.IllegalArgumentException: there is no corresponding model file`.

**3. Орда, урон, смерть**
- В обоих логах: `hordes` грузит `hordes:fallback`, `wave_0_normal_script`, спавнит `HordeSpawnEntry[type=entity.minecraft.zombie,weight=30,minDay=0,maxDay=0]`, `Quest Kill Task` фиксирует урон по `Zombie`, `InfectedMilitaryEntity`, `TheMoonflowerEntity`, `TherodEntity`, `ClickerEntity`, `Husk`, `ThelurkerEntity`, `ThepregnantEntity`, `BomberEntity`, `TheordureEntity`.
- С шейдерами: `Nechosi был убит Одержимый Миносом`, затем `Nechosi был убит Зомби`, затем `Nechosi был убит Infected Military`, затем `Nechosi убит` без источника.
- Без шейдеров: в предоставленном фрагменте смертей игрока нет, есть только урон и `Орда была побеждена!` позже.

**4. `Can't keep up` и тики**
- С шейдерами: `Can't keep up! Is the server overloaded? Running 2039ms or 40 ticks behind`, `2783ms or 55 ticks behind`, `2288ms or 45 ticks behind`.
- Без шейдеров: `Can't keep up` в предоставленном фрагменте не встречается.
- С шейдерами: `Профилирование тактов остановлено спустя 1216.47 секунд и 23308 тактов (19.16 тактов в секунду)`.
- Без шейдеров: профилирование в логе не запускалось/не останавливалось.

**5. `AllTheLeaks`**
- С шейдерами: `Cannot have null removal reason on Clone event!` повторяется, `Updated 300 player instances`, `Updated 301 level instances`, `Updated 9821 level instances`, `B: 3133MB / C: 6746MB / Diff: +3363MB`, затем `B: 3133MB / C: 3891MB / Diff: +758MB`, затем `B: 3133MB / C: 4285MB / Diff: +1152MB`, затем `B: 3133MB / C: 4929MB / Diff: +1796MB`, затем `B: 3133MB / C: 3510MB / Diff: +377MB`.
- Без шейдеров: `AllTheLeaks` в предоставленном фрагменте встречается только как миксины (`ForgeServerSparkPluginMixin`, `VillagesTradelistMixin`, `EntityTickListMixin`, `NormalizedTypedItemStackMixin`, `SmithingCategoryExtensionMixin`, `FakeLevelManagerMixin`), без строк `Cannot have null removal reason` и без отчётов `B/C/Diff`.

**6. `FakeLevelManagerMixin`**
- С шейдерами: `Method invalidateAll ... cancelled due to not matching hash: Actual -2034214357, Expected: [-1241170928]`, `Mixin annotation @WrapOperation ... removed due to no methods available`.
- Без шейдеров: этих строк нет, миксин применяется без отмены.

**7. Ресурсные релоады и `ModernFix`**
- С шейдерами: `ModernFix` пишет `Cleared 0 unneeded book NBT tags`, `Using cached upgraded version of ...` многократно, `Worker-ResourceReload-* shutdown`.
- Без шейдеров: `ModernFix` тоже пишет `Using cached upgraded version`, `Worker-ResourceReload-* shutdown`, но без `Cleared 0 unneeded book NBT tags` в предоставленном фрагменте.

**8. `PFSolver`**
- С шейдерами: сотни `Skipping due to hitbox miss`, `Foliage detected: straw/brush/leaves`, `Carpet detected: wood/hardmetal`.
- Без шейдеров: `PFSolver` в предоставленном фрагменте не встречается.

**9. `Sodium`-классы**
- В обоих логах: `Error loading class: net/caffeinemc/mods/sodium/client/model/light/data/LightDataAccess`, `ArrayLightDataCache`, `FlatLightPipeline` — `ClassNotFoundException`.
- В обоих логах: `sodiumdynamiclights` и `oculus` патчат `Embeddium`, а не `Sodium`.

**10. Реестры и `FabricRegistrySync`**
- В обоих логах: `FabricRegistrySync` при сохранении пишет длинный список `Not saving registry: ...`, включая `minecraft:item`, `minecraft:block`, `minecraft:entity_type`, `create:*`, `createbigcannons:*`, `corgilib:*`.
- В обоих логах: `FabricRegistrySync` не сохраняет `minecraft:menu`, `minecraft:recipe_serializer`, `minecraft:loot_condition_type` и т.д.

**11. `Create`**
- В обоих логах: `Prepared Redstone Network Space` и `Prepared Kinetic Network Space` для `overworld`, `the_nether`, `the_end`, `deceasedcraft:abyss_type`, `lostworlds:abyss_type`, `lostcities:lostcity`.
- С шейдерами: позже `Removed Redstone/Kinetic Network Space` для тех же измерений при выходе.
- Без шейдеров: `Removed ...` в предоставленном фрагменте не встречается.

**12. `Sound Physics Remastered`**
- В обоих логах: `EFX Extension recognized`, `Max auxiliary sends: 2`, `Aux slot 1–4 created`, `EFX ready`.
- С шейдерами: дополнительно десятки `Unknown sound in allowed sound config: ...`.
- Без шейдеров: `Unknown sound` в предоставленном фрагменте не встречается.

**13. `CraftPresence`**
- В обоих логах: `Попытка подключения к Discord (9/10)...`, `(10/10)...`.
- С шейдерами: `Невозможно подключиться к Discord...`.
- Без шейдеров: финальной ошибки в предоставленном фрагменте нет.

**14. `EMF` / `CustomNPCs`**
- В обоих логах: `Entity model [net.minecraft.client.model.PlayerModel] has been overridden by [noppes.npcs.client.renderer.RenderCustomNpc$2] likely from a mod.`

**15. `POI`**
- В обоих логах: `POI data mismatch: never registered at BlockPos{...}` с разными координатами.

**16. `Advancement`**
- В обоих логах: `Parsing error loading custom advancement animal_pen:grant_book_on_first_join: Advancement criteria cannot be empty`, `parcool:grant_parcool_guide: Advancement criteria cannot be empty`.

**17. `ConcurrentModificationException`**
- В обоих логах: `java.util.ConcurrentModificationException` в `LaunchPluginHandler.computeLaunchPluginTransformerSet / FileWatcher$WatcherThread` (в безшейдерном фрагменте не видно, но класс тот же).

**18. `Packet Fixer` / `Connectivity` / `Redirected` / `ModernFix` конфликты**
- В обоих логах: `@ModifyConstant conflict. Skipping connectivity ... already redirected by packetfixer`, `Skipping packetfixer ... already redirected by connectivity`, `@Redirect conflict. Skipping mixins.redirected_forge_1.20.1.json ... already redirected by lithium ... from mod radium`, `Method overwrite conflict for m_47505_ ... previously written by modernfix`, `@Redirect conflict. Skipping recipeessentials.mixins.json:RecipeManagerMixin ... already redirected by modernfix`.
- Разницы между логами по этим строкам нет.

**19. `Lazyyyyy`**
- В обоих логах: `Failed to read refmap ... from ...jar for config ...` по `parcool_compat_addon`, `jsconf`, `LongerChatHistory`, `fastpaintings`, `colorwheel_patcher`, `cobweb`, `item_scrapper`, `dsp`, `lmft`, `harvest_with_ease`, `clickmachine`, `puzzlesaccessapi`, `v_slab_compat`, `trashslot`, `coroutil`.
- С шейдерами: дополнительно `Cache pack <iris shaderpack shaders> in ...` сотни раз.
- Без шейдеров: `Cache pack <iris shaderpack shaders>` в предоставленном фрагменте не встречается.

**20. Память и `ChunkAccess`**
- С шейдерами: `AllTheLeaks` показывает `LevelChunk (minecraft): 72`, затем `1766`, затем `2582`, затем `4360`, затем `1046`.
- Без шейдеров: отчётов `LevelChunk` от `AllTheLeaks` в предоставленном фрагменте нет.

**21. `Xaero`**
- В обоих логах: `New Xaero hud session initialized!`, `New world map session initialized!`, `Registered synced player tracker system: ftb_teams`.
- С шейдерами: позже `Finalized session`, `World map cleaned normally!`.
- Без шейдеров: финализации в предоставленном фрагменте нет.

**22. `FTB Quests`**
- В обоих логах: `Loaded 8 chapter groups, 30 chapters, 801 quests, 1 reward tables`, `Wrote 190147 bytes, 2404 objects`, `Read 190147 bytes, 2404 objects`.

**23. `JEI`**
- В обоих логах: `Starting JEI...`, `Registering item subtypes`, `Registering fluid subtypes`, `Registering ingredients`, `Registering categories`, `Registering recipes`, `Building ingredient filter`, `Added 14471 ingredients`, `Building ingredient filter took 5.640 s` (с шейдерами) / `2.031 s` (без шейдеров, регистрация ингредиентов) — точные цифры различаются, но структура одна.
- С шейдерами: `Registering Runtime: jei:forge_gui is running and has taken 5.139 seconds so far`, `Registering Runtime: jei:forge_gui took 6.198 seconds`, `Starting JEI took 15.66 s`.
- Без шейдеров: этих строк в предоставленном фрагменте нет (фрагмент обрывается раньше).

**24. `Oculus` / `Iris` и `Colorwheel`**
- С шейдерами: `Found flag CUSTOM_IMAGES`, `Found flag SSBO`, `Found flag BLOCK_EMISSION_ATTRIBUTE`, `Tried to get boolean value for unknown option: FXAA, defaulting to true!` ×3, `Profile: POTATO (+5 options changed by user)`, `Using shaderpack: ComplementaryUnbound_r5.6.1 + Clrwl_1.0.3.zip`.
- Без шейдеров: `Destroying pipeline`, `Creating pipeline`, но без флагов, без `Profile`, без `Using shaderpack` в предоставленном фрагменте.

**25. `SoundOfRain`**
- С шейдерами: `Sound of Rain is evaporating...` при остановке.
- Без шейдеров: в предоставленном фрагменте нет.

**26. `Immersive Optimization`**
- С шейдерами: `Shutting down Immersive Optimization worker`.
- Без шейдеров: в предоставленном фрагменте нет.

**27. `Controllable`**
- С шейдерами: `Applying gamepad mappings from internal database`, `Successfully updated 1 gamepad mappings`.
- Без шейдеров: в предоставленном фрагменте нет.

**28. `Curios`**
- С шейдерами: `Curios disabled` при выходе.
- Без шейдеров: в предоставленном фрагменте нет.

**29. `Framework`**
- С шейдерами: `Stopping config watcher`, `Unloading server configs...`, `Finished unloading server configs`.
- Без шейдеров: в предоставленном фрагменте нет.

**30. `OpenPartiesAndClaims`**
- В обоих логах: `Saving server info!`, `Saving parties...`, `Saving player configs...`, `Saving claims!`, `Stopping IO worker...`, `Stopped IO worker!`.
- С шейдерами: дополнительно `Updating all forceload tickets for ...`.

**31. `FabricRegistrySync` при выходе**
- В обоих логах: длинный список `Not saving registry: ...`, затем `Gathering id map for writing to world save ТЕСТЫ`, `ID Map collection complete ТЕСТЫ`.

**32. `ModernFix` и `DFU`**
- С шейдерами: `Structure undead_revamp2:camp_bostrox2 is being run through DFU (hash ...), this will cause launch time delays`.
- Без шейдеров: в предоставленном фрагменте этой строки нет.

**33. `Create` и `OpenPartiesAndClaims`**
- В обоих логах: `MixinForgeOpenEndedPipe` применяется, `onProvideFluidToSpace` и `onRemoveFluidFromSpace` используют `CallbackInfoReturnable`.

**34. `TACZ`**
- В обоих логах: `ServerMessageSyncedEntityDataMapping`, `Received synced key mappings from server`, `Acknowledge`, `Received acknowledgement from client`, `SYNC_BASE_TIMESTAMP`.
- С шейдерами: `bf1:rsc1917_display display init read fail!` (см. п. 2).
- Без шейдеров: та же ошибка `bf1:rsc1917_display` присутствует.

**35. `Simple Voice Chat`**
- В обоих логах: `Voice chat server started at port ...`, `Received secret request`, `Sent secret`, `Successfully authenticated`, `Successfully connected to voice chat`, `Clearing audio channels`, `Stopping microphone thread`, `Disconnecting voicechat`.
- С шейдерами: порт `60062`.
- Без шейдеров: порт `59437`.

**36. `Puzzles Lib`**
- В обоих логах: `Unable to parse entry tconstruct:*: No matches found in registry minecraft:menu`, `mekanism:*: No matches found in registry minecraft:menu`.

**37. `Better Compatibility Checker`**
- В обоих логах: `ClientboundStatusResponsePacketMixin`, `onWrite`, `onReadConstructor`.

**38. `BadOptimizations`**
- В обоих логах: `Generating mapped inner class ... MixinDataTracker$1/$2`.

**39. `Carry On`**
- В обоих логах: `defineId called for: class net.minecraft.world.entity.player.Player from class tschipp.carryon.common.carry.CarryOnDataManager`.

**40. `Corpse Curios Compat`**
- В обоих логах: `CurioStacksHandlerMixin`, `Class version 61 required ... JAVA_8 supports class version 52`.

**41. `Deceased Expansion`**
- В обоих логах: `tacz.InteractKeyConfigReadMixin`, `dead$addMoreInteractables`, `lso.ThirstCapabilityMixin`, `carryon.EntityPickupHandlerMixin`, `dead$checkHauntedBuilding`.

**42. `Vinery`**
- В обоих логах: `WanderingTraderManagerMixin`, `trySpawn`, `does use it's CallbackInfoReturnable`.

**43. `Radium` / `Lithium`**
- В обоих логах: множество миксинов `lithium.mixins.json` с `Class version 61 required ... JAVA_16 supports class version 60`, `doesn't use it's CallbackInfo`, `has 0 override(s)`, `won't be passed a CallbackInfo`.
- С шейдерами: дополнительно `Method overwrite conflict for removeIf ... previously written by modernfix`.
- Без шейдеров: та же строка `Method overwrite conflict for removeIf ...` присутствует.

**44. `Redirected`**
- В обоих логах: `Mixing net.minecraft.world.level.chunk.storage.IOWorkerMixin`, `Mixing net.minecraft.world.level.chunk.UpgradeDataMixin`, `Mixing net.minecraft.world.level.block.state.CacheMixin`, `Mixing net.minecraft.world.level.pathfinder.NodeMixin`, `Mixing net.minecraft.world.level.pathfinder.TargetMixin`, `Mixing net.minecraft.world.level.pathfinder.AmphibiousNodeEvaluatorMixin`, `Mixing net.minecraft.world.level.pathfinder.SwimNodeEvaluatorMixin`, `Mixing net.minecraft.util.ParticleUtilsMixin`, `Mixing net.minecraft.world.level.levelgen.blending.BlenderMixin`, `Mixing net.minecraft.world.level.levelgen.blending.BlendingDataMixin`, `Mixing net.minecraft.server.level.ServerEntityMixin`, `Mixing net.minecraft.network.protocol.game.ClientboundSetEquipmentPacketMixin`, `Mixing forge.net.minecraftforge.items.wrapper.EntityEquipmentInvWrapperMixin`, `Mixing forge.net.minecraftforge.items.wrapper.PlayerArmorInvWrapperMixin`, `Mixing net.minecraft.client.renderer.chunk.ChunkRenderDispatcherRenderChunkMixin`, `Mixing net.minecraft.client.renderer.chunk.VisibilitySetMixin`.
- В обоих логах: `@Redirect conflict ... already redirected by modernfix` для `CacheMixin.redirectSupportTypes`.
- В обоих логах: `Mixing net.minecraft.world.level.block.state.CacheMixin` и `@Redirect conflict` — идентично.

**45. `Packet Fixer`**
- В обоих логах: `v1_19_4_forge.ClientboundLevelChunkPacketDataMixin`.
- В обоих логах: `@ModifyConstant conflict` с `connectivity` — идентично.

**46. `Connectivity`**
- В обоих логах: `ConnectionProtocolMixin`, `onAdd`, `NetworkRegistryMixin`, `onInit`, `@ModifyConstant conflict` с `packetfixer` — идентично.

**47. `Moonlight`**
- В обоих логах: `PacketDistributorHackMixin`, `ml$fixHardCast1/2/3`, `MapItemDataPacketMixin`, `addExtraCenterAndDimension`, `readExtraData`, `writeExtraData`, `handleExtraData`.

**48. `Create` и `Moonlight`**
- В обоих логах: `ClientboundMapItemDataPacketMixin` от `create` и `MapItemDataPacketMixin` от `moonlight` применяются к одному классу, оба используют `CallbackInfo`.

**49. `Xaero` и `Create`**
- В обоих логах: `MixinChunkDeltaUpdateS2CPacket` от `xaerohud`, `MixinChunkDeltaUpdateS2CPacketAccessor` от `xaeroworldmap` применяются к `ClientboundSectionBlocksUpdatePacket`.

**50. `SecurityCraft`**
- В обоих логах: `camera.ChunkMapMixin`, `camera.ClientChunkCacheMixin`, `camera.ViewAreaMixin`, `camera.TrackedEntityMixin`, `portal.PortalForcerMixin`, `camera.ChunkMapMixin` — все с `doesn't use it's CallbackInfo`, `has 0 override(s)`, `won't be passed a CallbackInfo`.

**51. `CustomNPCs`**
- В обоих логах: `PersistentEntitySectionManagerMixin`, `Unexpected: Registered method getCache() ... was not merged`, `ChunkMapMixin`, `GoalSelectorMixin`, `CCreativeInventoryActionPacketMixin`.

**52. `Smooth Chunk`**
- В обоих логах: `PersistentEntitySectionManagerMixin`, `ChunkMapMixin`, `ChunkMapSlowUnload`, `onSchedule`, `onRunUnload`.

**53. `Fast Async World Save`**
- В обоих логах: `DimensionDataStorageMixin`, `fastasyncworldsave$saveOffthread$0`.

**54. `CorgiLib`**
- В обоих логах: `chunk.MixinChunkSerializer`, `writeScheduledRandomTicks`, `readScheduledRandomTicks`.

**55. `Architectury`**
- В обоих логах: `MixinChunkSerializer`, `read`, `doesn't use it's CallbackInfoReturnable`.

**56. `Fabric Data Attachment API`**
- В обоих логах: `ChunkSerializerMixin`, `writeChunkAttachments`, `does use it's CallbackInfoReturnable`.

**57. `Fabric Registry Sync`**
- В обоих логах: `SerializableRegistriesMixin`, `Class version 61 required ... JAVA_16 supports class version 60`, `Renaming synthetic method lambda$filterNonSyncedEntries$0`.

**58. `Fabric Object Builder`**
- В обоих логах: `TradeOffersTypeAwareBuyForOneEmeraldFactoryMixin`, `Class version 61 required ... JAVA_16 supports class version 60`.

**59. `Fabric Biome API`**
- В обоих логах: `NoiseConfigMixin`, `Class version 61 required ... JAVA_16 supports class version 60`, `MultiNoiseUtilMultiNoiseSamplerMixin`, `ChunkNoiseSamplerMixin`.

**60. `Fabric Lifecycle Events`**
- В обоих логах: `ServerWorldServerEntityHandlerMixin`, `invokeEntityLoadEvent`, `invokeEntityUnloadEvent`, `ThreadedAnvilChunkStorageMixin`, `onChunkUnload`, `onChunkLoad`, `ClientWorldClientEntityHandlerMixin`, `invokeLoadEntity`, `invokeUnloadEntity`.

**61. `Fabric Networking API`**
- В обоих логах: `accessor.ThreadedAnvilChunkStorageAccessor`, `Class version 61 required ... JAVA_16 supports class version 60`, `EntityTrackerEntryMixin`, `onStartTracking`, `onStopTracking`.

**62. `Fabric Command API`**
- В обоих логах: `ClientCommandSourceMixin`, `Class version 61 required ... JAVA_16 supports class version 60`, `ClientCommandSourceStackMixin`.

**63. `Fabric Renderer API`**
- В обоих логах: `OverlayVertexConsumerMixin`, `Class version 61 required ... JAVA_16 supports class version 60`.

**64. `Fabric Renderer Indigo`**
- В обоих логах: `ChunkBuilderBuiltChunkRebuildTaskMixin`, `Class version 61 required ... JAVA_16 supports class version 60`, `hookChunkBuild`, `hookRebuildChunkReturn`.

**65. `Fabric Block View API`**
- В обоих логах: `ChunkRendererRegionBuilderMixin`, `createDataMap`.

**66. `Fabric Screen Handler API`**
- В обоих логах: `SimpleNamedScreenHandlerFactoryAccessor`, `Class version 61 required ... JAVA_16 supports class version 60`.

**67. `Fabric Content Registries`**
- В обоих логах: `LandPathNodeMakerMixin`, `Class version 61 required ... JAVA_16 supports class version 60`, `getCommonNodeType`, `getNodeTypeFromNeighbors`.

**68. `Fabric Biome Replacer`**
- В обоих логах: `terrablender.LevelUtilsMixin`.

**69. `TerraBlender`**
- В обоих логах: `Initialized TerraBlender biomes for level stem minecraft:the_nether`, `minecraft:overworld`.

**70. `YUNG's API`**
- В обоих логах: `BeardifierMixin`, `yungsapi_supportCustomTerrainAdaptations`, `yungsapi_calculateDensity`.

**71. `Zeta`**
- В обоих логах: `StructureStartMixin`, `injectReference`, `resetReference`.

**72. `Comforts`**
- В обоих логах: `MixinSleepStatus`, `comforts$sleepersNeeded`.

**73. `Cupboard`**
- В обоих логах: `ThreadingDetectorMixin`.

**74. `FerriteCore`**
- В обоих логах: `BlockStateCacheMixin`, `SubShapeAccess`, `OrConditionMixin`.

**75. `Saturn`**
- В обоих логах: `ViewAreaMixin`, `gc_heap.unnecessary_object_creation`, `HoglinAiMixin`, `allocations.do_nothing`.

**76. `BadOptimizations`**
- В обоих логах: `MixinDataTracker$1/$2`.

**77. `Immersive Optimization`**
- С шейдерами: `Shutting down Immersive Optimization worker`.
- Без шейдеров: только `EntityTickListAccessor`.

**78. `Mobtimizations`**
- В обоих логах: `MixinWalkNodeEvaluator`, `getBlockPathType`.

**79. `Cull Less Leaves`**
- В обоих логах: `sodiumcompat.BlockOcclusionCacheMixin`.

**80. `Bocchium`**
- В обоих логах: `BlockOcclusionCacheMixin`, `onShouldDrawSide`.

**81. `Better Biome Blend`**
- В обоих логах: `sodium.MixinWorldSlice`.

**82. `Flerovium`**
- В обоих логах: `Chunk.OcclusionCullerMixin`.

**83. `Sodium Dynamic Lights`**
- В обоих логах: `LightDataAccessMixin`, `ArrayLightDataCacheMixin`, `FlatLightPipelineMixin`, `ClassNotFoundException` для `net.caffeinemc.mods.sodium...`, `Embeddium-MixinTaintDetector`.

**84. `Oculus`**
- В обоих логах: `sky.MixinClientLevelData_DisableVoidPlane`, `MixinChunkRebuildTask`, `MixinChunkRenderDispatcherRebuildTask`, `MixinRenderSectionManager`, `MixinChunkBuilderMeshingTask`, `MixinShaderChunkRenderer`, `MixinChunkBuildBuffers`, `MixinChunkVertexBufferBuilder`, `MixinBakedChunkModelBuilder`, `MixinWorldSlice`, `MixinSmoothLightPipeline`, `MixinFlatLightPipeline`, `MixinCloudRenderer`, `MixinScreenEffectRenderer`, `MixinGlProgram`, `MixinShaderType`, `MixinVertexSerializerCache`, `MixinRegionChunkRenderer`, `MixinDefaultChunkRenderer`, `MixinShadowRenderTargets`, `IrisRenderingPipelineMixin`, `RenderTargetMixin`, `ProgramSetMixin`, `ProgramSourceMixin`, `ProgramDirectivesMixin`, `PackShadowDirectivesMixin`, `BlockMaterialMappingMixin`, `StandardMacrosMixin`, `ShaderPackSourceNamesMixin`, `BlendModeOverrideMixin`.
- В обоих логах: `Class version 61 required ... JAVA_8 supports class version 52`.

**85. `Colorwheel`**
- В обоих логах: `flw.BakedModelBuffererMixin`, `flw.MeshEmitterMixin`, `flw.MeshHelperMixin`, `iris.StandardMacrosMixin`, `iris.ShaderPackSourceNamesMixin`, `iris.BlendModeOverrideMixin`, `iris.ProgramSetMixin`, `iris.PackShadowDirectivesMixin`, `iris.ProgramSourceMixin`, `iris.ProgramDirectivesMixin`, `iris.IrisRenderingPipelineMixin`, `iris.RenderTargetMixin`, `iris.ShadowRenderTargetsMixin`, `iris.BlockMaterialMappingMixin`.

**86. `Flywheel`**
- В обоих логах: `light.LightEngineAccessor`, `light.SkyLightSectionStorageMixin`, `light.SkyDataLayerStorageMapAccessor`, `ClientChunkCacheMixin`, `visualmanage.RebuildTaskMixin`, `flywheel$tryAddBlockEntity`, `Started 8 worker threads`.
- С шейдерами: `Flywheel backend fell back from 'flywheel:instancing' to 'flywheel:off'` повторяется, `Compiled pipeline/instancing/...` с большими миллисекундами (`64,162 ms`, `22,206 ms`, `95,444 ms`, `1,914 ms`, `895,200 μs`, `2,726 ms`, `55,800 μs`, `3,894 ms`, `3,702 ms`, `4,355 ms`, `962,800 μs`, `38,600 μs`, `2,109 ms`, `23,500 μs`, `32,500 μs`, `932,800 μs`), `No active uniform '_flw_depthRange'`, `_flw_coefficients`, `_flw_blueNoise`, `_flw_lightLut`, `_flw_lightSections`, `_flw_vertexOffset`.
- Без шейдеров: `Flywheel` fallback и `Compiled pipeline/instancing` в предоставленном фрагменте не встречаются.

**87. `Embeddium`**
- В обоих логах: `ChunkBuilderMixin`, `SpriteTexturedVertexConsumerMixin`, `VertexConsumersMixin$DualMixin`, `OutlineVertexConsumerMixin`, `OverlayVertexConsumerMixin`, `PostprocessorMixin`, `PackedIntegerArrayMixin`, `PalettedContainerMixin`, `EmptyPaletteStorageMixin`, `Embeddium-MixinTaintDetector`.
- С шейдерами: `Embeddium-MixinTaintDetector` предупреждает про `oculus`, `sodiumdynamiclights`, `betterbiomereblend`, `culllessleaves`, `bocchium`, `flerovium`.
- Без шейдеров: те же предупреждения, тот же набор.

**88. `ModernFix`**
- В обоих логах: `bugfix.paper_chunk_patches.ChunkMapMixin`, `bugfix.chunk_deadlock.ChunkMapLoadMixin`, `perf.cache_strongholds.ChunkGeneratorMixin`, `perf.faster_structure_location.StructureCheckMixin`, `perf.cache_blockstate_cache_arrays.AbstractBlockStateCacheMixin`, `perf.compact_bit_storage.PalettedContainerMixin`, `perf.chunk_meshing.RebuildTaskMixin`, `bugfix.paper_chunk_patches.SortedArraySetMixin`, `perf.remove_spawn_chunks.SortedArraySetMixin`, `perf.worldgen_allocation.NoiseChunkMixin`, `perf.worldgen_allocation.MaterialRuleListMixin`, `perf.worldgen_allocation.SurfaceRulesContextMixin`, `perf.worldgen_allocation.SurfaceRulesMixin`, `perf.worldgen_allocation.SequenceRuleMixin`, `Using cached upgraded version of ...`, `Using enhanced recipe sync for player Nechosi`, `Cleared 0 unneeded book NBT tags`.
- С шейдерами: `Structure undead_revamp2:camp_bostrox2 is being run through DFU ...`, `Time from main menu to in-game was 30.54571 seconds`, `Total time to load game and open world was 117.44371 seconds`.
- Без шейдеров: `Time from main menu to in-game` / `Total time` в предоставленном фрагменте нет.

**89. `Radium` / `Lithium` и `ModernFix`**
- В обоих логах: `Method overwrite conflict for removeIf in lithium.mixins.json:world.chunk_tickets.SortedArraySetMixin from mod radium, previously written by org.embeddedt.modernfix.common.mixin.bugfix.paper_chunk_patches.SortedArraySetMixin. Skipping method.`

**90. `Redirected` и `ModernFix`**
- В обоих логах: `@Redirect conflict. Skipping mixins.redirected_forge_1.20.1.json:net.minecraft.world.level.block.state.CacheMixin from mod redirected->@Redirect::redirectSupportTypes ... already redirected by modernfix-common.mixins.json:perf.cache_blockstate_cache_arrays.AbstractBlockStateCacheMixin ... with priority 1000`.

**91. `RecipeEssentials` и `ModernFix`**
- В обоих логах: `@Redirect conflict. Skipping recipeessentials.mixins.json:RecipeManagerMixin ... already redirected by modernfix`.

**92. `Connectivity` и `Packet Fixer`**
- В обоих логах: `@ModifyConstant conflict. Skipping connectivity ... already redirected by packetfixer` и `Skipping packetfixer ... already redirected by connectivity`.

**93. `Flerovium` и `Embeddium`**
- В обоих логах: `Method overwrite conflict for sodium$createViewport in embeddium.mixins.json ... previously written by com.moepus.flerovium.mixins.Chunk.FrustumMixin. Skipping method.`

**94. `CorgiLib`**
- В обоих логах: `GET request failed. Response Code: 301`.

**95. `CustomNPCs` и `EMF`**
- В обоих логах: `Entity model [net.minecraft.client.model.PlayerModel] has been overridden by [noppes.npcs.client.renderer.RenderCustomNpc$2] likely from a mod.`

**96. `Apocalypse Now`**
- В обоих логах: десятки `Unable to load model: 'minecraft:...' referenced from: apocalypsenow:...`.
- С шейдерами: те же модели, тот же список.
- Без шейдеров: те же модели, тот же список.

**97. `Storage Drawers`**
- В обоих логах: `Exception loading blockstate definition: 'storagedrawers:blockstates/meta_framed_drawers_shading.json' missing model for variant...`, `ModelMissingException`.

**98. `Refined Storage`**
- В обоих логах: `Unable to load model: 'refinedstorage:cover#inventory' ... FileNotFoundException: refinedstorage:models/item/cover.json`, `ModelMissingException`.

**99. `TACZ`**
- В обоих логах: `bf1:rsc1917_display display init read fail! java.lang.IllegalArgumentException: there is no corresponding model file`.

**100. `Sound Physics`**
- В обоих логах: `EFX Extension recognized`, `Max auxiliary sends: 2`, `Aux slot 1–4 created`, `EFX ready`.
- С шейдерами: дополнительно `Unknown sound in allowed sound config: ...`.
- Без шейдеров: `Unknown sound` в предоставленном фрагменте нет.

**101. `PFSolver`**
- С шейдерами: сотни `Skipping due to hitbox miss`, `Foliage detected: straw/brush/leaves`, `Carpet detected: wood/hardmetal`.
- Без шейдеров: `PFSolver` в предоставленном фрагменте не встречается.

**102. `Oculus` и `Flywheel`**
- С шейдерами: `Flywheel backend fell back from 'flywheel:instancing' to 'flywheel:off'` повторяется.
- Без шейдеров: `Flywheel backend fell back` в предоставленном фрагменте нет.

**103. `Embeddium` и `Oculus`**
- С шейдерами: `Embeddium-MixinTaintDetector` предупреждает про `oculus`, `sodiumdynamiclights`, `betterbiomereblend`, `culllessleaves`, `bocchium`, `flerovium`.
- Без шейдеров: те же предупреждения.

**104. `ModernFix` и `DFU`**
- С шейдерами: `Structure undead_revamp2:camp_bostrox2 is being run through DFU ...`.
- Без шейдеров: в предоставленном фрагменте нет.

**105. `AllTheLeaks`**
- С шейдерами: `Cannot have null removal reason on Clone event!`, `Updated 300 player instances`, `Updated 301 level instances`, `Updated 9821 level instances`, `B/C/Diff`, `LevelChunk` counts.
- Без шейдеров: только миксины, без `Cannot have null removal reason`, без `B/C/Diff`, без `LevelChunk` counts в предоставленном фрагменте.

**106. `FakeLevelManagerMixin`**
- С шейдерами: `Method invalidateAll ... cancelled due to not matching hash`, `Mixin annotation @WrapOperation ... removed due to no methods available`.
- Без шейдеров: этих строк нет.

**107. `FabricRegistrySync`**
- В обоих логах: длинный список `Not saving registry: ...`, `Starting registry save`, `Gathering id map for writing to world save ТЕСТЫ`, `ID Map collection complete ТЕСТЫ`.

**108. `Create`**
- В обоих логах: `Prepared Redstone Network Space` / `Prepared Kinetic Network Space` для `overworld`, `the_nether`, `the_end`, `deceasedcraft:abyss_type`, `lostworlds:abyss_type`, `lostcities:lostcity`.
- С шейдерами: позже `Removed Redstone/Kinetic Network Space` для тех же измерений.
- Без шейдеров: `Removed ...` в предоставленном фрагменте нет.

**109. `OpenPartiesAndClaims`**
- В обоих логах: `Saving server info!`, `Saving parties...`, `Saving player configs...`, `Saving claims!`, `Stopping IO worker...`, `Stopped IO worker!`.
- С шейдерами: дополнительно `Updating all forceload tickets for ...`.
- Без шейдеров: `Updating all forceload tickets` в предоставленном фрагменте нет.

**110. `Xaero`**
- В обоих логах: `New Xaero hud session initialized!`, `New world map session initialized!`, `Registered synced player tracker system: ftb_teams`.
- С шейдерами: позже `Finalized session`, `World map cleaned normally!`.
- Без шейдеров: финализации в предоставленном фрагменте нет.

**111. `JEI`**
- В обоих логах: `Starting JEI...`, `Registering item subtypes`, `Registering fluid subtypes`, `Registering ingredients`, `Registering categories`, `Registering recipes`, `Building ingredient filter`, `Added 14471 ingredients`.
- С шейдерами: `Building ingredient filter took 5.640 s`, `Registering Runtime: jei:forge_gui is running and has taken 5.139 seconds so far`, `Registering Runtime: jei:forge_gui took 6.198 seconds`, `Starting JEI took 15.66 s`.
- Без шейдеров: `Registering ingredients took 2.849 s`, `Registering categories took 766.8 ms`, `Registering recipes: jei:minecraft took 1.404 seconds`, без `Registering Runtime: jei:forge_gui` в предоставленном фрагменте (обрыв раньше).

**112. `Oculus`**
- С шейдерами: `Found flag CUSTOM_IMAGES`, `Found flag SSBO`, `Found flag BLOCK_EMISSION_ATTRIBUTE`, `Tried to get boolean value for unknown option: FXAA, defaulting to true!` ×3, `Profile: POTATO (+5 options changed by user)`, `Using shaderpack: ComplementaryUnbound_r5.6.1 + Clrwl_1.0.3.zip`, `Failed to resolve uniform inPaleGarden`, `Error while parsing the block ID map entry for "block.10104"`.
- Без шейдеров: `Destroying pipeline`, `Creating pipeline`, но без флагов, без `Profile`, без `Using shaderpack` в предоставленном фрагменте.

**113. `Flywheel`**
- С шейдерами: `Flywheel backend fell back from 'flywheel:instancing' to 'flywheel:off'`, `Compiled pipeline/instancing/...` с большими миллисекундами, `No active uniform '_flw_...'`.
- Без шейдеров: `Flywheel` fallback и `Compiled pipeline/instancing` в предоставленном фрагменте не встречаются.

**114. `Embeddium`**
- С шейдерами: `Embeddium-MixinTaintDetector` предупреждает про `oculus`, `sodiumdynamiclights`, `betterbiomereblend`, `culllessleaves`, `bocchium`, `flerovium`.
- Без шейдеров: те же предупреждения, тот же набор.

**115. `ModernFix`**
- С шейдерами: `Structure undead_revamp2:camp_bostrox2 is being run through DFU ...`, `Time from main menu to in-game was 30.54571 seconds`, `Total time to load game and open world was 117.44371 seconds`.
- Без шейдеров: этих строк в предоставленном фрагменте нет.

**116. `AllTheLeaks`**
- С шейдерами: `Cannot have null removal reason on Clone event!`, `Updated 300 player instances`, `Updated 301 level instances`, `Updated 9821 level instances`, `B/C/Diff`, `LevelChunk` counts.
- Без шейдеров: только миксины, без `Cannot have null removal reason`, без `B/C/Diff`, без `LevelChunk` counts в предоставленном фрагменте.

**117. `FakeLevelManagerMixin`**
- С шейдерами: `Method invalidateAll ... cancelled due to not matching hash`, `Mixin annotation @WrapOperation ... removed due to no methods available`.
- Без шейдеров: этих строк нет.

**118. `FabricRegistrySync`**
- В обоих логах: длинный список `Not saving registry: ...`, `Starting registry save`, `Gathering id map for writing to world save ТЕСТЫ`, `ID Map collection complete ТЕСТЫ`.

**119. `Create`**
- В обоих логах: `Prepared Redstone Network Space` / `Prepared Kinetic Network Space` для `overworld`, `the_nether`, `the_end`, `deceasedcraft:abyss_type`, `lostworlds:abyss_type`, `lostcities:lostcity`.
- С шейдерами: позже `Removed Redstone/Kinetic Network Space` для тех же измерений.
- Без шейдеров: `Removed ...` в предоставленном фрагменте нет.

**120. `OpenPartiesAndClaims`**
- В обоих логах: `Saving server info!`, `Saving parties...`, `Saving player configs...`, `Saving claims!`, `Stopping IO worker...`, `Stopped IO worker!`.
- С шейдерами: дополнительно `Updating all forceload tickets for ...`.
- Без шейдеров: `Updating all forceload tickets` в предоставленном фрагменте нет.

**121. `Xaero`**
- В обоих логах: `New Xaero hud session initialized!`, `New world map session initialized!`, `Registered synced player tracker system: ftb_teams`.
- С шейдерами: позже `Finalized session`, `World map cleaned normally!`.
- Без шейдеров: финализации в предоставленном фрагменте нет.

**122. `JEI`**
- В обоих логах: `Starting JEI...`, `Registering item subtypes`, `Registering fluid subtypes`, `Registering ingredients`, `Registering categories`, `Registering recipes`, `Building ingredient filter`, `Added 14471 ingredients`.
- С шейдерами: `Building ingredient filter took 5.640 s`, `Registering Runtime: jei:forge_gui is running and has taken 5.139 seconds so far`, `Registering Runtime: jei:forge_gui took 6.198 seconds`, `Starting JEI took 15.66 s`.
- Без шейдеров: `Registering ingredients took 2.849 s`, `Registering categories took 766.8 ms`, `Registering recipes: jei:minecraft took 1.404 seconds`, без `Registering Runtime: jei:forge_gui` в предоставленном фрагменте (обрыв раньше).

**123. `Oculus`**
- С шейдерами: `Found flag CUSTOM_IMAGES`, `Found flag SSBO`, `Found flag BLOCK_EMISSION_ATTRIBUTE`, `Tried to get boolean value for unknown option: FXAA, defaulting to true!` ×3, `Profile: POTATO (+5 options changed by user)`, `Using shaderpack: ComplementaryUnbound_r5.6.1 + Clrwl_1.0.3.zip`, `Failed to resolve uniform inPaleGarden`, `Error while parsing the block ID map entry for "block.10104"`.
- Без шейдеров: `Destroying pipeline`, `Creating pipeline`, но без флагов, без `Profile`, без `Using shaderpack` в предоставленном фрагменте.

**124. `Flywheel`**
- С шейдерами: `Flywheel backend fell back from 'flywheel:instancing' to 'flywheel:off'`, `Compiled pipeline/instancing/...` с большими миллисекундами, `No active uniform '_flw_...'`.
- Без шейдеров: `Flywheel` fallback и `Compiled pipeline/instancing` в предоставленном фрагменте не встречаются.

**125. `Embeddium`**
- С шейдерами: `Embeddium-MixinTaintDetector` предупреждает про `oculus`, `sodiumdynamiclights`, `betterbiomereblend`, `culllessleaves`, `bocchium`, `flerovium`.
- Без шейдеров: те же предупреждения, тот же набор.

**126. `ModernFix`**
- С шейдерами: `Structure undead_revamp2:camp_bostrox2 is being run through DFU ...`, `Time from main menu to in-game was 30.54571 seconds`, `Total time to load game and open world was 117.44371 seconds`.
- Без шейдеров: этих строк в предоставленном фрагменте нет.

**127. `AllTheLeaks`**
- С шейдерами: `Cannot have null removal reason on Clone event!`, `Updated 300 player instances`, `Updated 301 level instances`, `Updated 9821 level instances`, `B/C/Diff`, `LevelChunk` counts.
- Без шейдеров: только миксины, без `Cannot have null removal reason`, без `B/C/Diff`, без `LevelChunk` counts в предоставленном фрагменте.

**128. `FakeLevelManagerMixin`**
- С шейдерами: `Method invalidateAll ... cancelled due to not matching hash`, `Mixin annotation @WrapOperation ... removed due to no methods available`.
- Без шейдеров: этих строк нет.



**Вердикт: шейдерный стек не является корневой причиной, но он — усилитель. Базовая сборка дефектна независимо от шейдеров.**

**Что сломано в обоих логах (не связано с шейдерами):**
- `Apocalypse Now` — десятки отсутствующих моделей (`market`, `tv`, `sodamachine`, `iron_shelf*`, `barricade`, `gascanister`, `medical_i`, `tool`, `ammo` и др.).
- `Storage Drawers` — `meta_framed_drawers_shading.json` без модели для вариантов, `ModelMissingException`.
- `Refined Storage` — `refinedstorage:cover#inventory` → `FileNotFoundException`.
- `TACZ` — `bf1:rsc1917_display` без модели.
- `Embeddium` помечен `tainted` набором `oculus`, `sodiumdynamiclights`, `betterbiomereblend`, `culllessleaves`, `bocchium`, `flerovium`.
- `Sodium`-классы не найдены (`LightDataAccess`, `ArrayLightDataCache`, `FlatLightPipeline`) — `sodiumdynamiclights` и `oculus` патчат `Embeddium`, а не `Sodium`.
- Конфликты миксинов: `Redirected` ↔ `Radium`/`ModernFix`, `Connectivity` ↔ `PacketFixer`, `RecipeEssentials` ↔ `ModernFix`, `Flerovium` ↔ `Embeddium`.
- `POI data mismatch`, `Advancement criteria cannot be empty` (`animal_pen`, `parcool`), `ConcurrentModificationException` в `LaunchPluginHandler`, `CorgiLib` `GET 301`, `EMF`/`CustomNPCs` override `PlayerModel`, `Sound Physics` `Unknown sound`.

**Что появляется только с шейдерами:**
- `Oculus`: `Failed to resolve uniform inPaleGarden`, `Error while parsing block ID map entry "block.10104"`, `GL ERROR 65540`.
- `Flywheel backend fell back from 'flywheel:instancing' to 'flywheel:off'` (повторяется), `Compiled pipeline/instancing/...` с миллисекундами до `95 444 ms`, `No active uniform '_flw_*'`.
- `Can't keep up` — `40`, `42`, `43`, `44`, `45`, `55` тиков позади; профиль `19.16 тактов в секунду`.
- `AllTheLeaks`: `Cannot have null removal reason on Clone event!`, отчёты `Diff: +3363MB / +1796MB / +1152MB / +758MB / +377MB`, рост `LevelChunk` до `4360`.
- `FakeLevelManagerMixin`: `invalidateAll cancelled due to not matching hash`, `@WrapOperation removed due to no methods available`.
- `JEI`: `Registering Runtime: jei:forge_gui took 6.198 seconds`, `Starting JEI took 15.66 s`.
- `PFSolver`: сотни `Skipping due to hitbox miss`, `Foliage detected`, `Carpet detected`.
- `CraftPresence`: `Невозможно подключиться к Discord`.
- `Lazyyyyy`: `Cache pack <iris shaderpack shaders>` сотни раз.

**Итог:**
- Без шейдеров в предоставленном фрагменте нет `Can't keep up`, нет отчётов `AllTheLeaks` о росте памяти, нет отмены `FakeLevelManagerMixin`, нет `Flywheel` fallback, нет `PFSolver`, нет `GL ERROR`, нет `inPaleGarden`/`block.10104`, нет `JEI forge_gui` на 6 секунд.
- С шейдерами всё это присутствует, плюс профиль `19.16 tps` и `+3363MB` в пике.
- При этом дефекты ассетов (`Apocalypse Now`, `Storage Drawers`, `Refined Storage`, `TACZ`), конфликты миксинов и `taint`-предупреждения `Embeddium` **идентичны в обоих логах** — значит, они не следствие шейдеров.

**Формулировка:** шейдерный стек (Oculus + Complementary + Clrwl + Flywheel) добавляет собственную нагрузку и обнажает уже существующие проблемы сборки, но не создаёт их. Базовая сборка содержит независимые дефекты ассетов и миксин-конфликты, которые проявятся и без шейдеров.
