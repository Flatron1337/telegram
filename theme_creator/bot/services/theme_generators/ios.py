from __future__ import annotations

from bot.models.color import PaletteTheme

_IOS_THEME_TEMPLATE = """name: "{name}"
basedOn: day
dark: {dark_str}
intro:
statusBar: {status_bar}
primaryText: {txt}
accentText: {accent}
disabledText: 33{txt_sec}
startButton: {accent}
dot: 5e5e5e
passcode:
  bg:
    top: {bg}
    bottom: {bg}
  button: clear
root:
  statusBar: {status_bar}
  tabBar:
    background: {bg}
    separator: 33{accent}
    icon: a1{accent}
    selectedIcon: {accent}
    text: a1{accent}
    selectedText: {accent}
    badgeBackground: {txt}
    badgeStroke: {bg}
    badgeText: {bg}
  navBar:
    button: {accent}
    disabledButton: 33{accent}
    primaryText: {txt}
    secondaryText: {txt_sec}
    control: {accent}
    accentText: {accent}
    background: {bg}
    separator: 33{accent}
    badgeFill: {txt}
    badgeStroke: {bg}
    badgeText: {acc_txt}
  searchBar:
    background: {bg}
    accent: {accent}
    inputFill: 33{bg}
    inputText: {txt}
    inputPlaceholderText: a1{accent}
    inputIcon: 33{txt}
    inputClearButton: {txt_sec}
    separator: 33{accent}
  keyboard: {keyboard}
list:
  blocksBg: {bg}
  plainBg: {bg}
  primaryText: {txt}
  secondaryText: {txt_sec}
  disabledText: 1e{accent}
  accent: {accent}
  highlighted: 1e{accent}
  destructive: ff3b30
  placeholderText: c8c8ce
  itemBlocksBg: {bg}
  itemHighlightedBg: 1e{accent}
  blocksSeparator: 33{accent}
  plainSeparator: 33{accent}
  disclosureArrow: bab9be
  sectionHeaderText: 6d6d72
  freeText: 6d6d72
  freeTextError: cf3030
  freeTextSuccess: 26972c
  freeMonoIcon: 7e7e87
  switch:
    frame: e0e0e0
    handle: ffffff
    content: 77d572
    positive: 00c900
    negative: ff3b30
  disclosureActions:
    neutral1:
      bg: 4892f2
      fg: ffffff
    neutral2:
      bg: f09a37
      fg: ffffff
    destructive:
      bg: ff3824
      fg: ffffff
    constructive:
      bg: 00c900
      fg: ffffff
    accent:
      bg: {accent}
      fg: {acc_txt}
    warning:
      bg: ff9500
      fg: ffffff
    inactive:
      bg: bcbcc3
      fg: ffffff
  check:
    bg: {accent}
    stroke: c7c7cc
    fg: {acc_txt}
  controlSecondary: dedede
  freeInputField:
    bg: {bg}
    stroke: {bg}
    placeholder: 96979d
    primary: {txt}
    control: {accent}
  mediaPlaceholder: e4e4e4
  scrollIndicator: 4c000000
  pageIndicatorInactive: e3e3e7
  inputClearButton: cccccc
chatList:
  bg: {bg}
  itemSeparator: 33{accent}
  itemBg: 1ed6d6d6
  pinnedItemBg: {bg}
  itemHighlightedBg: 1e{accent}
  itemSelectedBg: 1e{accent}
  title: {txt}
  secretTitle: 00b12c
  dateText: {txt_sec}
  authorName: {txt_sec}
  messageText: {txt_sec}
  messageDraftText: {txt_sec}
  checkmark: {accent}
  pendingIndicator: {txt_sec}
  failedFill: ff3b30
  failedFg: ffffff
  muteIcon: {txt_sec}
  unreadBadgeActiveBg: {accent}
  unreadBadgeActiveText: {acc_txt}
  unreadBadgeInactiveBg: b6b6bb
  unreadBadgeInactiveText: ffffff
  pinnedBadge: {accent}
  pinnedSearchBar: e5e5e5
  regularSearchBar: e9e9e9
  sectionHeaderBg: 33d6d6d6
  sectionHeaderText: 8e8e93
  verifiedIconBg: {accent}
  verifiedIconFg: {acc_txt}
  secretIcon: 00b12c
  pinnedArchiveAvatar:
    background:
      top: 1e{accent}
      bottom: {accent}
    foreground: {acc_txt}
  unpinnedArchiveAvatar:
    background:
      top: 1e{txt_sec}
      bottom: {txt_sec}
    foreground: {acc_txt}
  onlineDot: 4cc91f
chat:
  defaultWallpaper: {bg}
  message:
    incoming:
      bubble:
        withWp:
          bg: {in_b_alpha}{in_b}
          highlightedBg: {in_b_hi_alpha}{in_b}
          stroke: {in_b_alpha}{in_b}
        withoutWp:
          bg: {in_b}
          highlightedBg: {in_b_hi_alpha}{in_b}
          stroke: {in_b}
      primaryText: {in_txt}
      secondaryText: a5{in_txt_sec}
      linkText: {accent}
      linkHighlight: 1e{accent}
      scam: ff3b30
      textHighlight: 1e{accent}
      accentText: {accent}
      accentControl: {accent}
      mediaActiveControl: {accent}
      mediaInactiveControl: {txt_sec}
      pendingActivity: 99{in_txt}
      fileTitle: {accent}
      fileDescription: a5{in_txt_sec}
      fileDuration: 99{in_txt_sec}
      mediaPlaceholder: f2f2f2
      polls:
        radioButton: c8c7cc
        radioProgress: {accent}
        highlight: 1e{accent}
        separator: c8c7cc
        bar: {accent}
      actionButtonsBg:
        withWp: 66a5a5a5
        withoutWp: cc{in_b}
      actionButtonsStroke:
        withWp: clear
        withoutWp: {accent}
      actionButtonsText:
        withWp: {in_txt}
        withoutWp: {accent}
      textSelection: 4c{accent}
      textSelectionKnob: {accent}
    outgoing:
      bubble:
        withWp:
          bg: {out_b_alpha}{out_b}
          highlightedBg: {out_b_hi_alpha}{out_b}
          stroke: {out_b_alpha}{out_b}
        withoutWp:
          bg: {out_b}
          highlightedBg: {out_b_hi_alpha}{out_b}
          stroke: {out_b}

      primaryText: {out_txt}
      secondaryText: a5{out_txt_sec}
      linkText: {out_txt}
      linkHighlight: 4c{out_txt}
      scam: {out_txt}
      textHighlight: 4c{out_txt}
      accentText: {out_txt}
      accentControl: {out_txt}
      mediaActiveControl: {out_txt}
      mediaInactiveControl: a5{out_txt_sec}
      pendingActivity: a5{out_txt_sec}
      fileTitle: {out_txt}
      fileDescription: a5{out_txt_sec}
      fileDuration: a5{out_txt_sec}
      mediaPlaceholder: 0000f2
      polls:
        radioButton: a5{out_txt_sec}
        radioProgress: {out_txt}
        highlight: 1e{out_txt}
        separator: a5{out_txt_sec}
        bar: {out_txt}
      actionButtonsBg:
        withWp: 66a5a5a5
        withoutWp: cc{in_b}
      actionButtonsStroke:
        withWp: clear
        withoutWp: {accent}
      actionButtonsText:
        withWp: {out_txt}
        withoutWp: {accent}
      textSelection: 33{out_txt}
      textSelectionKnob: {out_txt}
    freeform:
      withWp:
        bg: e5e5ea
        highlightedBg: dadade
        stroke: e5e5ea
      withoutWp:
        bg: e5e5ea
        highlightedBg: dadade
        stroke: e5e5ea
    infoPrimaryText: {txt}
    infoLinkText: {accent}
    outgoingCheck: {out_txt}
    mediaDateAndStatusBg: 7f000000
    mediaDateAndStatusText: ffffff
    shareButtonBg:
      withWp: 66a5a5a5
      withoutWp: cc{in_b}
    shareButtonStroke:
      withWp: clear
      withoutWp: e5e5ea
    shareButtonFg:
      withWp: ffffff
      withoutWp: {accent}
    mediaOverlayControl:
      bg: 99000000
      fg: ffffff
    selectionControl:
      bg: {accent}
      stroke: c7c7cc
      fg: {acc_txt}
    deliveryFailed:
      bg: ff3b30
      fg: ffffff
    mediaHighlightOverlay: 99ffffff
  serviceMessage:
    components:
      withDefaultWp:
        bg: cc{bg}
        primaryText: {txt_sec}
        linkHighlight: 3f{accent}
        scam: ff3b30
        dateFillStatic: cc{bg}
        dateFillFloat: cc{bg}
      withCustomWp:
        bg: 66a5a5a5
        primaryText: ffffff
        linkHighlight: 3f{accent}
        scam: ff3b30
        dateFillStatic: 66a5a5a5
        dateFillFloat: 44a5a5a5
    unreadBarBg: {bg}
    unreadBarStroke: {bg}
    unreadBarText: {txt_sec}
    dateText:
      withWp: ffffff
      withoutWp: {txt_sec}
  inputPanel:
    panelBg: {bg}
    panelSeparator: 33{accent}
    panelControlAccent: {accent}
    panelControl: {txt_sec}
    panelControlDisabled: 1e{txt_sec}
    panelControlDestructive: ff3b30
    inputBg: 1ed6d6d6
    inputStroke: {bg}
    inputPlaceholder: 33{txt_sec}
    inputText: {txt}
    inputControl: {accent}
    actionControlBg: {accent}
    actionControlFg: {acc_txt}
    primaryText: {txt}
    secondaryText: {txt_sec}
    mediaRecordDot: {accent}
    mediaRecordControl:
      button: {accent}
      micLevel: 1e{accent}
      activeIcon: {acc_txt}
  inputMediaPanel:
    panelSeparator: bec2c6
    panelIcon: 858e99
    panelHighlightedIconBg: 33858e99
    stickersBg: e8ebf0
    stickersSectionText: 9099a2
    stickersSearchBg: d9dbe1
    stickersSearchPlaceholder: 8e8e93
    stickersSearchPrimary: 000000
    stickersSearchControl: 8e8e93
    gifsBg: ffffff
  inputButtonPanel:
    panelBg: dee2e6
    panelSeparator: bec2c6
    buttonBg: ffffff
    buttonStroke: c3c7c9
    buttonHighlightedBg: a8b3c0
    buttonHighlightedStroke: c3c7c9
    buttonText: 000000
  historyNav:
    bg: {bg}
    stroke: {bg}
    fg: {txt}
    badgeBg: {accent}
    badgeStroke: {accent}
    badgeText: {acc_txt}
actionSheet:
  dim: 66000000
  bgType: {bg_type}
  opaqueItemBg: {actionsheet_bg}
  itemBg: dd{actionsheet_bg}
  opaqueItemHighlightedBg: e5e5e5
  itemHighlightedBg: b2e5e5e5
  opaqueItemSeparator: e5e5e5
  standardActionText: {accent}
  destructiveActionText: ff3b30
  disabledActionText: b3b3b3
  primaryText: {txt}
  secondaryText: {txt_sec}
  controlAccent: {accent}
  inputBg: e9e9e9
  inputHollowBg: {actionsheet_bg}
  inputBorder: e4e4e6
  inputPlaceholder: 818086
  inputText: {txt}
  inputClearButton: 7b7b81
  checkContent: {acc_txt}
contextMenu:
  dim: 99000000
  background: c6252525
  itemSeparator: 26ffffff
  sectionSeparator: 33000000
  itemBg: 00000000
  itemHighlightedBg: 26ffffff
  primary: ffffff
  secondary: ccffffff
  destructive: eb5545
notification:
  bg: {bg}
  primaryText: {txt}
  expanded:
    bgType: {bg_type}
    navBar:
      background: {bg}
      primaryText: {txt}
      control: {txt_sec}
      separator: b1b1b1
"""


class IosThemeGenerator:
    """Generates Telegram iOS theme files (.tgios-theme) in valid YAML format."""

    def generate_theme_text(
        self,
        theme: PaletteTheme,
        name: str = "Custom Theme",
    ) -> str:
        """Render complete .tgios-theme YAML specification matching Telegram iOS architecture."""
        is_dark = theme.is_dark
        in_alpha = getattr(theme, "in_bubble_alpha", 255)
        out_alpha = getattr(theme, "out_bubble_alpha", 255)
        in_hi = max(0, in_alpha - 40)
        out_hi = max(0, out_alpha - 40)

        return _IOS_THEME_TEMPLATE.format(
            name=name.replace('"', '\\"'),
            dark_str="true" if is_dark else "false",
            status_bar="black" if is_dark else "white",
            keyboard="dark" if is_dark else "light",
            bg_type="dark" if is_dark else "light",
            actionsheet_bg="252525" if is_dark else "ffffff",
            bg=theme.surface.hex[1:],
            accent=theme.accent.hex[1:],
            txt=theme.text_primary.hex[1:],
            txt_sec=theme.text_secondary.hex[1:],
            acc_txt=theme.accent_text.hex[1:],
            in_b=theme.in_bubble.hex[1:],
            in_b_alpha=f"{in_alpha:02x}",
            in_b_hi_alpha=f"{in_hi:02x}",
            in_txt=theme.in_bubble_text.hex[1:],
            in_txt_sec=theme.in_bubble_subtext.hex[1:],
            out_b=theme.out_bubble.hex[1:],
            out_b_alpha=f"{out_alpha:02x}",
            out_b_hi_alpha=f"{out_hi:02x}",
            out_txt=theme.out_bubble_text.hex[1:],
            out_txt_sec=theme.out_bubble_subtext.hex[1:],
        )


    def generate_theme_package(
        self,
        theme: PaletteTheme,
        name: str = "Custom Theme",
    ) -> bytes:
        """Create standard UTF-8 encoded .tgios-theme payload for Telegram iOS."""
        return self.generate_theme_text(theme, name=name).encode("utf-8")
