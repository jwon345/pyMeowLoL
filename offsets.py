ObjIndex = 0x08#13.1
ObjTeam = 0x34#13.1
ObjPlayerName = 0x54#13.1
ObjNetworkID = 0xB4#13.1
ObjPos = 0x1DC#13.1
ObjVisibility = 0x274#13.1
ObjSpawnCount = 0x288#13.1
ObjSrcIndex = 0x294#13.1
ObjMana = 0x29C#13.1
ObjMaxMana = 0x2AC#13.1
ObjHealth = 0xE7C#13.1
ObjMaxHealth = 0xE8C#13.1
ObjArmor = 0x1384#13.1
ObjBonusArmor = 0x1388 #13.1 
ObjMagicRes = 0x138C#13.1
ObjBonusMagicRes = 0x1390 #13.1
ObjBaseAtk = 0x135C#13.1
ObjBonusAtk = 0x12D4#13.1
ObjMoveSpeed = 0x139C#13.1
ObjSpellBook = 0x29D0#13.1
ObjName = 0x2DBC#13.1
ObjLvl = 0x35AC#13.1
ObjExpiry = 0x298#13.1
ObjCrit = 0x1858#13.1
ObjCritMulti = 0x12D4#13.1
ObjAbilityPower = 0x1758#13.1
ObjAtkSpeedMulti = 0x132C#13.1 ??
ObjItemList = 0x35F8 #13.1
ObjAIManager = 0x2E94 #13.1
ObjInvulnerable = 0x3D4 #13.1
ObjIsTargetable = 0xD04 #13.1
ObjIsTargetableToTeam = 0xD14 #13.1
ObjIsBasing = 0xD90 #13.1
ObjBuffManager = 0x2340 #13.1
ObjCombatType = 0x2270 #13.1
ObjEnemyID = 0x2EBC #13.1
ObjRemainingPoint = 0x35D4 #13.1
ObjCastSpell = 0x2528 #13.1
ObjManaQ = 0x2560 #13.1
ObjManaW = 0x2570 #13.1
ObjManaE = 0x2580 #13.1
ObjManaR = 0x2590 #13.1

objAtkRange = 0x13A4

ItemListItem = 0xC
ItemInfo = 0x20
ItemInfoId = 0x74
 
RendererWidth = 0x8
RendererHeight = 0xc
 
SpellSotLevel = 0x1C
SpellSlotTime = 0x24
SpellSlotDamage = 0x94
SpellSlotSpellInfo = 0x120
 
SpellInfoSpellData = 0x40
 
SpellDataSpellName = 0x6C
SpellDataMissileName = 0x6C
 
ObjectMapCount = 0x2C
ObjectMapRoot = 0x28
ObjectMapNodeNetId = 0x10
ObjectMapNodeObject = 0x14
 
MissileSpellInfo = 0x0260
MissileSrcIdx = 0x2C4
MissileDestIdx = 0x318
MissileStartPos = 0x2E0
MissileEndPos = 0x2EC
 
MinimapObject = 0x3143C88
MinimapObjectHud = 0x15C
MinimapHudPos = 0x3C
MinimapHudSize = 0x44
 
#SpellEntry
oSpellEntrySpellInfo = 0x8
oSpellEntryIndex = 0x14
oSpellEntrySlot = 0xC
oSpellEntryStartPos = 0x80
oSpellEntryEndPos = 0x8C
oSpellEntryIsBasicAttack = 0xBC
oSpellEntryWindupTime = 0x4C0
oSpellEntryCastStartTime = 0x544
 
#SpellInfo
oSpellInfoSpellName = 0x6C
oSpellInfoSpellData = 0x40
 
#SpellData
oSpellDataRange = 0x3C0
oSpellDataCastRadius = 0x3F8
oSpellDataSpeed = 0x44C
oSpellDataWidth = 0x474
oSpellDataMana = 0x524
 
#IDA
GameTime = 0x315CCF4#13.1
 
ViewProjMatrices = 0x3189D00#13.1
Renderer = 0x318F6A0#13.1
 
ObjectManager = 0x18C6B1C#13.1
LocalPlayer = 0x3163080#13.1
UnderMouseObject = 0x2514404#13.1
 
IssueOrder = 0x167340#13.1
SpoofGadget = 0xF71F9D#13.1 # ff 23 jmp dword ptr [ebx]
 
NewCastSpell = 0x672520# 13.1
GetSpellState = 0x51E4A0# 13.1
 
IsHero = 0x19F880 #13.1 #1000h 
IsMinion = 0x19F8C0 #13.1 #800h 
IsTurret = 0x19F9B0 #13.1 #2000h
IsMissile = 0x19F8E0 #13.1 #8000h 
IsInhibitor = 0x19F820 #13.1 #2th
IsNexus = 0x19F860 #13.1 #3th
IsAlive = 0x190530 # 13.1
IsNotWall = 0xA3F000# 13.1
 
HudInstance = 0x18C6B24#13.1
GetBoundRadius = 0x15ACD0 # 13.1
BuildNavFunction = 0xA35E70 # 13.1
SmoothPathFunction = 0x1DB2D0 #13.1
 
ModSkinFunction = 0xBEE8C0 # 13.1
SendChatFunction = 0x6722D0 # 13.1 
 
AttackDelayFunction = 0x296E40 # 13.1
BasicAttackFunction = 0x15A410 # 13.1
AttackCastDelayFunction = 0x296D40 # 13.1
 
ChatInstance = 0x3163F94 # 13.1
ZoomHackInstance = 0x315C398 # 13.1
 
NetClientInstance = 0x3168F54 # 13.1
GetPing = 0x35CBD0 #13.1