/**
 * @popperjs/core v2.11.8 - MIT License
 */

(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
  typeof define === 'function' && define.amd ? define(['exports'], factory) :
  (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.Popper = {}));
}(this, (function (exports) { 'use strict';

  function getWindow(node) {
    if (node == null) {
      return window;
    }

    if (node.toString() !== '[object Window]') {
      var ownerDocument = node.ownerDocument;
      return ownerDocument ? ownerDocument.defaultView || window : window;
    }

    return node;
  }

  function isElement(node) {
    var OwnElement = getWindow(node).Element;
    return node instanceof OwnElement || node instanceof Element;
  }

  function isHTMLElement(node) {
    var OwnElement = getWindow(node).HTMLElement;
    return node instanceof OwnElement || node instanceof HTMLElement;
  }

  function isShadowRoot(node) {
    // IE 11 has no ShadowRoot
    if (typeof ShadowRoot === 'undefined') {
      return false;
    }

    var OwnElement = getWindow(node).ShadowRoot;
    return node instanceof OwnElement || node instanceof ShadowRoot;
  }

  var max = Math.max;
  var min = Math.min;
  var round = Math.round;

  function getUAString() {
    var uaData = navigator.userAgentData;

    if (uaData != null && uaData.brands && Array.isArray(uaData.brands)) {
      return uaData.brands.map(function (item) {
        return item.brand + "/" + item.version;
      }).join(' ');
    }

    return navigator.userAgent;
  }

  function isLayoutViewport() {
    return !/^((?!chrome|android).)*safari/i.test(getUAString());
  }

  function getBoundingClientRect(element, includeScale, isFixedStrategy) {
    if (includeScale === void 0) {
      includeScale = false;
    }

    if (isFixedStrategy === void 0) {
      isFixedStrategy = false;
    }

    var clientRect = element.getBoundingClientRect();
    var scaleX = 1;
    var scaleY = 1;

    if (includeScale && isHTMLElement(element)) {
      scaleX = element.offsetWidth > 0 ? round(clientRect.width) / element.offsetWidth || 1 : 1;
      scaleY = element.offsetHeight > 0 ? round(clientRect.height) / element.offsetHeight || 1 : 1;
    }

    var _ref = isElement(element) ? getWindow(element) : window,
        visualViewport = _ref.visualViewport;

    var addVisualOffsets = !isLayoutViewport() && isFixedStrategy;
    var x = (clientRect.left + (addVisualOffsets && visualViewport ? visualViewport.offsetLeft : 0)) / scaleX;
    var y = (clientRect.top + (addVisualOffsets && visualViewport ? visualViewport.offsetTop : 0)) / scaleY;
    var width = clientRect.width / scaleX;
    var height = clientRect.height / scaleY;
    return {
      width: width,
      height: height,
      top: y,
      right: x + width,
      bottom: y + height,
      left: x,
      x: x,
      y: y
    };
  }

  function getWindowScroll(node) {
    var win = getWindow(node);
    var scrollLeft = win.pageXOffset;
    var scrollTop = win.pageYOffset;
    return {
      scrollLeft: scrollLeft,
      scrollTop: scrollTop
    };
  }

  function getHTMLElementScroll(element) {
    return {
      scrollLeft: element.scrollLeft,
      scrollTop: element.scrollTop
    };
  }

  function getNodeScroll(node) {
    if (node === getWindow(node) || !isHTMLElement(node)) {
      return getWindowScroll(node);
    } else {
      return getHTMLElementScroll(node);
    }
  }

  function getNodeName(element) {
    return element ? (element.nodeName || '').toLowerCase() : null;
  }

  function getDocumentElement(element) {
    // $FlowFixMe[incompatible-return]: assume body is always available
    return ((isElement(element) ? element.ownerDocument : // $FlowFixMe[prop-missing]
    element.document) || window.document).documentElement;
  }

  function getWindowScrollBarX(element) {
    // If <html> has a CSS width greater than the viewport, then this will be
    // incorrect for RTL.
    // Popper 1 is broken in this case and never had a bug report so let's assume
    // it's not an issue. I don't think anyone ever specifies width on <html>
    // anyway.
    // Browsers where the left scrollbar doesn't cause an issue report `0` for
    // this (e.g. Edge 2019, IE11, Safari)
    return getBoundingClientRect(getDocumentElement(element)).left + getWindowScroll(element).scrollLeft;
  }

  function getComputedStyle(element) {
    return getWindow(element).getComputedStyle(element);
  }

  function isScrollParent(element) {
    // Firefox wants us to check `-x` and `-y` variations as well
    var _getComputedStyle = getComputedStyle(element),
        overflow = _getComputedStyle.overflow,
        overflowX = _getComputedStyle.overflowX,
        overflowY = _getComputedStyle.overflowY;

    return /auto|scroll|overlay|hidden/.test(overflow + overflowY + overflowX);
  }

  function isElementScaled(element) {
    var rect = element.getBoundingClientRect();
    var scaleX = round(rect.width) / element.offsetWidth || 1;
    var scaleY = round(rect.height) / element.offsetHeight || 1;
    return scaleX !== 1 || scaleY !== 1;
  } // Returns the composite rect of an element relative to its offsetParent.
  // Composite means it takes into account transforms as well as layout.


  function getCompositeRect(elementOrVirtualElement, offsetParent, isFixed) {
    if (isFixed === void 0) {
      isFixed = false;
    }

    var isOffsetParentAnElement = isHTMLElement(offsetParent);
    var offsetParentIsScaled = isHTMLElement(offsetParent) && isElementScaled(offsetParent);
    var documentElement = getDocumentElement(offsetParent);
    var rect = getBoundingClientRect(elementOrVirtualElement, offsetParentIsScaled, isFixed);
    var scroll = {
      scrollLeft: 0,
      scrollTop: 0
    };
    var offsets = {
      x: 0,
      y: 0
    };

    if (isOffsetParentAnElement || !isOffsetParentAnElement && !isFixed) {
      if (getNodeName(offsetParent) !== 'body' || // https://github.com/popperjs/popper-core/issues/1078
      isScrollParent(documentElement)) {
        scroll = getNodeScroll(offsetParent);
      }

      if (isHTMLElement(offsetParent)) {
        offsets = getBoundingClientRect(offsetParent, true);
        offsets.x += offsetParent.clientLeft;
        offsets.y += offsetParent.clientTop;
      } else if (documentElement) {
        offsets.x = getWindowScrollBarX(documentElement);
      }
    }

    return {
      x: rect.left + scroll.scrollLeft - offsets.x,
      y: rect.top + scroll.scrollTop - offsets.y,
      width: rect.width,
      height: rect.height
    };
  }

  // means it doesn't take into account transforms.

  function getLayoutRect(element) {
    var clientRect = getBoundingClientRect(element); // Use the clientRect sizes if it's not been transformed.
    // Fixes https://github.com/popperjs/popper-core/issues/1223

    var width = element.offsetWidth;
    var height = element.offsetHeight;

    if (Math.abs(clientRect.width - width) <= 1) {
      width = clientRect.width;
    }

    if (Math.abs(clientRect.height - height) <= 1) {
      height = clientRect.height;
    }

    return {
      x: element.offsetLeft,
      y: element.offsetTop,
      width: width,
      height: height
    };
  }

  function getParentNode(element) {
    if (getNodeName(element) === 'html') {
      return element;
    }

    return (// this is a quicker (but less type safe) way to save quite some bytes from the bundle
      // $FlowFixMe[incompatible-return]
      // $FlowFixMe[prop-missing]
      element.assignedSlot || // step into the shadow DOM of the parent of a slotted node
      element.parentNode || ( // DOM Element detected
      isShadowRoot(element) ? element.host : null) || // ShadowRoot detected
      // $FlowFixMe[incompatible-call]: HTMLElement is a Node
      getDocumentElement(element) // fallback

    );
  }

  function getScrollParent(node) {
    if (['html', 'body', '#document'].indexOf(getNodeName(node)) >= 0) {
      // $FlowFixMe[incompatible-return]: assume body is always available
      return node.ownerDocument.body;
    }

    if (isHTMLElement(node) && isScrollParent(node)) {
      return node;
    }

    return getScrollParent(getParentNode(node));
  }

  /*
  given a DOM element, return the list of all scroll parents, up the list of ancesors
  until we get to the top window object. This list is what we attach scroll listeners
  to, because if any of these parent elements scroll, we'll need to re-calculate the
  reference element's position.
  */

  function listScrollParents(element, list) {
    var _element$ownerDocumen;

    if (list === void 0) {
      list = [];
    }

    var scrollParent = getScrollParent(element);
    var isBody = scrollParent === ((_element$ownerDocumen = element.ownerDocument) == null ? void 0 : _element$ownerDocumen.body);
    var win = getWindow(scrollParent);
    var target = isBody ? [win].concat(win.visualViewport || [], isScrollParent(scrollParent) ? scrollParent : []) : scrollParent;
    var updatedList = list.concat(target);
    return isBody ? updatedList : // $FlowFixMe[incompatible-call]: isBody tells us target will be an HTMLElement here
    updatedList.concat(listScrollParents(getParentNode(target)));
  }

  function isTableElement(element) {
    return ['table', 'td', 'th'].indexOf(getNodeName(element)) >= 0;
  }

  function getTrueOffsetParent(element) {
    if (!isHTMLElement(element) || // https://github.com/popperjs/popper-core/issues/837
    getComputedStyle(element).position === 'fixed') {
      return null;
    }

    return element.offsetParent;
  } // `.offsetParent` reports `null` for fixed elements, while absolute elements
  // return the containing block


  function getContainingBlock(element) {
    var isFirefox = /firefox/i.test(getUAString());
    var isIE = /Trident/i.test(getUAString());

    if (isIE && isHTMLElement(element)) {
      // In IE 9, 10 and 11 fixed elements containing block is always established by the viewport
      var elementCss = getComputedStyle(element);

      if (elementCss.position === 'fixed') {
        return null;
      }
    }

    var currentNode = getParentNode(element);

    if (isShadowRoot(currentNode)) {
      currentNode = currentNode.host;
    }

    while (isHTMLElement(currentNode) && ['html', 'body'].indexOf(getNodeName(currentNode)) < 0) {
      var css = getComputedStyle(currentNode); // This is non-exhaustive but covers the most common CSS properties that
      // create a containing block.
      // https://developer.mozilla.org/en-US/docs/Web/CSS/Containing_block#identifying_the_containing_block

      if (css.transform !== 'none' || css.perspective !== 'none' || css.contain === 'paint' || ['transform', 'perspective'].indexOf(css.willChange) !== -1 || isFirefox && css.willChange === 'filter' || isFirefox && css.filter && css.filter !== 'none') {
        return currentNode;
      } else {
        currentNode = currentNode.parentNode;
      }
    }

    return null;
  } // Gets the closest ancestor positioned element. Handles some edge cases,
  // such as table ancestors and cross browser bugs.


  function getOffsetParent(element) {
    var window = getWindow(element);
    var offsetParent = getTrueOffsetParent(element);

    while (offsetParent && isTableElement(offsetParent) && getComputedStyle(offsetParent).position === 'static') {
      offsetParent = getTrueOffsetParent(offsetParent);
    }

    if (offsetParent && (getNodeName(offsetParent) === 'html' || getNodeName(offsetParent) === 'body' && getComputedStyle(offsetParent).position === 'static')) {
      return window;
    }

    return offsetParent || getContainingBlock(element) || window;
  }

  var top = 'top';
  var bottom = 'bottom';
  var right = 'right';
  var left = 'left';
  var auto = 'auto';
  var basePlacements = [top, bottom, right, left];
  var start = 'start';
  var end = 'end';
  var clippingParents = 'clippingParents';
  var viewport = 'viewport';
  var popper = 'popper';
  var reference = 'reference';
  var variationPlacements = /*#__PURE__*/basePlacements.reduce(function (acc, placement) {
    return acc.concat([placement + "-" + start, placement + "-" + end]);
  }, []);
  var placements = /*#__PURE__*/[].concat(basePlacements, [auto]).reduce(function (acc, placement) {
    return acc.concat([placement, placement + "-" + start, placement + "-" + end]);
  }, []); // modifiers that need to read the DOM

  var beforeRead = 'beforeRead';
  var read = 'read';
  var afterRead = 'afterRead'; // pure-logic modifiers

  var beforeMain = 'beforeMain';
  var main = 'main';
  var afterMain = 'afterMain'; // modifier with the purpose to write to the DOM (or write into a framework state)

  var beforeWrite = 'beforeWrite';
  var write = 'write';
  var afterWrite = 'afterWrite';
  var modifierPhases = [beforeRead, read, afterRead, beforeMain, main, afterMain, beforeWrite, write, afterWrite];

  function order(modifiers) {
    var map = new Map();
    var visited = new Set();
    var result = [];
    modifiers.forEach(function (modifier) {
      map.set(modifier.name, modifier);
    }); // On visiting object, check for its dependencies and visit them recursively

    function sort(modifier) {
      visited.add(modifier.name);
      var requires = [].concat(modifier.requires || [], modifier.requiresIfExists || []);
      requires.forEach(function (dep) {
        if (!visited.has(dep)) {
          var depModifier = map.get(dep);

          if (depModifier) {
            sort(depModifier);
          }
        }
      });
      result.push(modifier);
    }

    modifiers.forEach(function (modifier) {
      if (!visited.has(modifier.name)) {
        // check for visited object
        sort(modifier);
      }
    });
    return result;
  }

  function orderModifiers(modifiers) {
    // order based on dependencies
    var orderedModifiers = order(modifiers); // order based on phase

    return modifierPhases.reduce(function (acc, phase) {
      return acc.concat(orderedModifiers.filter(function (modifier) {
        return modifier.phase === phase;
      }));
    }, []);
  }

  function debounce(fn) {
    var pending;
    return function () {
      if (!pending) {
        pending = new Promise(function (resolve) {
          Promise.resolve().then(function () {
            pending = undefined;
            resolve(fn());
          });
        });
      }

      return pending;
    };
  }

  function mergeByName(modifiers) {
    var merged = modifiers.reduce(function (merged, current) {
      var existing = merged[current.name];
      merged[current.name] = existing ? Object.assign({}, existing, current, {
        options: Object.assign({}, existing.options, current.options),
        data: Object.assign({}, existing.data, current.data)
      }) : current;
      return merged;
    }, {}); // IE11 does not support Object.values

    return Object.keys(merged).map(function (key) {
      return merged[key];
    });
  }

  function getViewportRect(element, strategy) {
    var win = getWindow(element);
    var html = getDocumentElement(element);
    var visualViewport = win.visualViewport;
    var width = html.clientWidth;
    var height = html.clientHeight;
    var x = 0;
    var y = 0;

    if (visualViewport) {
      width = visualViewport.width;
      height = visualViewport.height;
      var layoutViewport = isLayoutViewport();

      if (layoutViewport || !layoutViewport && strategy === 'fixed') {
        x = visualViewport.offsetLeft;
        y = visualViewport.offsetTop;
      }
    }

    return {
      width: width,
      height: height,
      x: x + getWindowScrollBarX(element),
      y: y
    };
  }

  // of the `<html>` and `<body>` rect bounds if horizontally scrollable

  function getDocumentRect(element) {
    var _element$ownerDocumen;

    var html = getDocumentElement(element);
    var winScroll = getWindowScroll(element);
    var body = (_element$ownerDocumen = element.ownerDocument) == null ? void 0 : _element$ownerDocumen.body;
    var width = max(html.scrollWidth, html.clientWidth, body ? body.scrollWidth : 0, body ? body.clientWidth : 0);
    var height = max(html.scrollHeight, html.clientHeight, body ? body.scrollHeight : 0, body ? body.clientHeight : 0);
    var x = -winScroll.scrollLeft + getWindowScrollBarX(element);
    var y = -winScroll.scrollTop;

    if (getComputedStyle(body || html).direction === 'rtl') {
      x += max(html.clientWidth, body ? body.clientWidth : 0) - width;
    }

    return {
      width: width,
      height: height,
      x: x,
      y: y
    };
  }

  function contains(parent, child) {
    var rootNode = child.getRootNode && child.getRootNode(); // First, attempt with faster native method

    if (parent.contains(child)) {
      return true;
    } // then fallback to custom implementation with Shadow DOM support
    else if (rootNode && isShadowRoot(rootNode)) {
        var next = child;

        do {
          if (next && parent.isSameNode(next)) {
            return true;
          } // $FlowFixMe[prop-missing]: need a better way to handle this...


          next = next.parentNode || next.host;
        } while (next);
      } // Give up, the result is false


    return false;
  }

  function rectToClientRect(rect) {
    return Object.assign({}, rect, {
      left: rect.x,
      top: rect.y,
      right: rect.x + rect.width,
      bottom: rect.y + rect.height
    });
  }

  function getInnerBoundingClientRect(element, strategy) {
    var rect = getBoundingClientRect(element, false, strategy === 'fixed');
    rect.top = rect.top + element.clientTop;
    rect.left = rect.left + element.clientLeft;
    rect.bottom = rect.top + element.clientHeight;
    rect.right = rect.left + element.clientWidth;
    rect.width = element.clientWidth;
    rect.height = element.clientHeight;
    rect.x = rect.left;
    rect.y = rect.top;
    return rect;
  }

  function getClientRectFromMixedType(element, clippingParent, strategy) {
    return clippingParent === viewport ? rectToClientRect(getViewportRect(element, strategy)) : isElement(clippingParent) ? getInnerBoundingClientRect(clippingParent, strategy) : rectToClientRect(getDocumentRect(getDocumentElement(element)));
  } // A "clipping parent" is an overflowable container with the characteristic of
  // clipping (or hiding) overflowing elements with a position different from
  // `initial`


  function getClippingParents(element) {
    var clippingParents = listScrollParents(getParentNode(element));
    var canEscapeClipping = ['absolute', 'fixed'].indexOf(getComputedStyle(element).position) >= 0;
    var clipperElement = canEscapeClipping && isHTMLElement(element) ? getOffsetParent(element) : element;

    if (!isElement(clipperElement)) {
      return [];
    } // $FlowFixMe[incompatible-return]: https://github.com/facebook/flow/issues/1414


    return clippingParents.filter(function (clippingParent) {
      return isElement(clippingParent) && contains(clippingParent, clipperElement) && getNodeName(clippingParent) !== 'body';
    });
  } // Gets the maximum area that the element is visible in due to any number of
  // clipping parents


  function getClippingRect(element, boundary, rootBoundary, strategy) {
    var mainClippingParents = boundary === 'clippingParents' ? getClippingParents(element) : [].concat(boundary);
    var clippingParents = [].concat(mainClippingParents, [rootBoundary]);
    var firstClippingParent = clippingParents[0];
    var clippingRect = clippingParents.reduce(function (accRect, clippingParent) {
      var rect = getClientRectFromMixedType(element, clippingParent, strategy);
      accRect.top = max(rect.top, accRect.top);
      accRect.right = min(rect.right, accRect.right);
      accRect.bottom = min(rect.bottom, accRect.bottom);
      accRect.left = max(rect.left, accRect.left);
      return accRect;
    }, getClientRectFromMixedType(element, firstClippingParent, strategy));
    clippingRect.width = clippingRect.right - clippingRect.left;
    clippingRect.height = clippingRect.bottom - clippingRect.top;
    clippingRect.x = clippingRect.left;
    clippingRect.y = clippingRect.top;
    return clippingRect;
  }

  function getBasePlacement(placement) {
    return placement.split('-')[0];
  }

  function getVariation(placement) {
    return placement.split('-')[1];
  }

  function getMainAxisFromPlacement(placement) {
    return ['top', 'bottom'].indexOf(placement) >= 0 ? 'x' : 'y';
  }

  function computeOffsets(_ref) {
    var reference = _ref.reference,
        element = _ref.element,
        placement = _ref.placement;
    var basePlacement = placement ? getBasePlacement(placement) : null;
    var variation = placement ? getVariation(placement) : null;
    var commonX = reference.x + reference.width / 2 - element.width / 2;
    var commonY = reference.y + reference.height / 2 - element.height / 2;
    var offsets;

    switch (basePlacement) {
      case top:
        offsets = {
          x: commonX,
          y: reference.y - element.height
        };
        break;

      case bottom:
        offsets = {
          x: commonX,
          y: reference.y + reference.height
        };
        break;

      case right:
        offsets = {
          x: reference.x + reference.width,
          y: commonY
        };
        break;

      case left:
        offsets = {
          x: reference.x - element.width,
          y: commonY
        };
        break;

      default:
        offsets = {
          x: reference.x,
          y: reference.y
        };
    }

    var mainAxis = basePlacement ? getMainAxisFromPlacement(basePlacement) : null;

    if (mainAxis != null) {
      var len = mainAxis === 'y' ? 'height' : 'width';

      switch (variation) {
        case start:
          offsets[mainAxis] = offsets[mainAxis] - (reference[len] / 2 - element[len] / 2);
          break;

        case end:
          offsets[mainAxis] = offsets[mainAxis] + (reference[len] / 2 - element[len] / 2);
          break;
      }
    }

    return offsets;
  }

  function getFreshSideObject() {
    return {
      top: 0,
      right: 0,
      bottom: 0,
      left: 0
    };
  }

  function mergePaddingObject(paddingObject) {
    return Object.assign({}, getFreshSideObject(), paddingObject);
  }

  function expandToHashMap(value, keys) {
    return keys.reduce(function (hashMap, key) {
      hashMap[key] = value;
      return hashMap;
    }, {});
  }

  function detectOverflow(state, options) {
    if (options === void 0) {
      options = {};
    }

    var _options = options,
        _options$placement = _options.placement,
        placement = _options$placement === void 0 ? state.placement : _options$placement,
        _options$strategy = _options.strategy,
        strategy = _options$strategy === void 0 ? state.strategy : _options$strategy,
        _options$boundary = _options.boundary,
        boundary = _options$boundary === void 0 ? clippingParents : _options$boundary,
        _options$rootBoundary = _options.rootBoundary,
        rootBoundary = _options$rootBoundary === void 0 ? viewport : _options$rootBoundary,
        _options$elementConte = _options.elementContext,
        elementContext = _options$elementConte === void 0 ? popper : _options$elementConte,
        _options$altBoundary = _options.altBoundary,
        altBoundary = _options$altBoundary === void 0 ? false : _options$altBoundary,
        _options$padding = _options.padding,
        padding = _options$padding === void 0 ? 0 : _options$padding;
    var paddingObject = mergePaddingObject(typeof padding !== 'number' ? padding : expandToHashMap(padding, basePlacements));
    var altContext = elementContext === popper ? reference : popper;
    var popperRect = state.rects.popper;
    var element = state.elements[altBoundary ? altContext : elementContext];
    var clippingClientRect = getClippingRect(isElement(element) ? element : element.contextElement || getDocumentElement(state.elements.popper), boundary, rootBoundary, strategy);
    var referenceClientRect = getBoundingClientRect(state.elements.reference);
    var popperOffsets = computeOffsets({
      reference: referenceClientRect,
      element: popperRect,
      strategy: 'absolute',
      placement: placement
    });
    var popperClientRect = rectToClientRect(Object.assign({}, popperRect, popperOffsets));
    var elementClientRect = elementContext === popper ? popperClientRect : referenceClientRect; // positive = overflowing the clipping rect
    // 0 or negative = within the clipping rect

    var overflowOffsets = {
      top: clippingClientRect.top - elementClientRect.top + paddingObject.top,
      bottom: elementClientRect.bottom - clippingClientRect.bottom + paddingObject.bottom,
      left: clippingClientRect.left - elementClientRect.left + paddingObject.left,
      right: elementClientRect.right - clippingClientRect.right + paddingObject.right
    };
    var offsetData = state.modifiersData.offset; // Offsets can be applied only to the popper element

    if (elementContext === popper && offsetData) {
      var offset = offsetData[placement];
      Object.keys(overflowOffsets).forEach(function (key) {
        var multiply = [right, bottom].indexOf(key) >= 0 ? 1 : -1;
        var axis = [top, bottom].indexOf(key) >= 0 ? 'y' : 'x';
        overflowOffsets[key] += offset[axis] * multiply;
      });
    }

    return overflowOffsets;
  }

  var DEFAULT_OPTIONS = {
    placement: 'bottom',
    modifiers: [],
    strategy: 'absolute'
  };

  function areValidElements() {
    for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
      args[_key] = arguments[_key];
    }

    return !args.some(function (element) {
      return !(element && typeof element.getBoundingClientRect === 'function');
    });
  }

  function popperGenerator(generatorOptions) {
    if (generatorOptions === void 0) {
      generatorOptions = {};
    }

    var _generatorOptions = generatorOptions,
        _generatorOptions$def = _generatorOptions.defaultModifiers,
        defaultModifiers = _generatorOptions$def === void 0 ? [] : _generatorOptions$def,
        _generatorOptions$def2 = _generatorOptions.defaultOptions,
        defaultOptions = _generatorOptions$def2 === void 0 ? DEFAULT_OPTIONS : _generatorOptions$def2;
    return function createPopper(reference, popper, options) {
      if (options === void 0) {
        options = defaultOptions;
      }

      var state = {
        placement: 'bottom',
        orderedModifiers: [],
        options: Object.assign({}, DEFAULT_OPTIONS, defaultOptions),
        modifiersData: {},
        elements: {
          reference: reference,
          popper: popper
        },
        attributes: {},
        styles: {}
      };
      var effectCleanupFns = [];
      var isDestroyed = false;
      var instance = {
        state: state,
        setOptions: function setOptions(setOptionsAction) {
          var options = typeof setOptionsAction === 'function' ? setOptionsAction(state.options) : setOptionsAction;
          cleanupModifierEffects();
          state.options = Object.assign({}, defaultOptions, state.options, options);
          state.scrollParents = {
            reference: isElement(reference) ? listScrollParents(reference) : reference.contextElement ? listScrollParents(reference.contextElement) : [],
            popper: listScrollParents(popper)
          }; // Orders the modifiers based on their dependencies and `phase`
          // properties

          var orderedModifiers = orderModifiers(mergeByName([].concat(defaultModifiers, state.options.modifiers))); // Strip out disabled modifiers

          state.orderedModifiers = orderedModifiers.filter(function (m) {
            return m.enabled;
          });
          runModifierEffects();
          return instance.update();
        },
        // Sync update – it will always be executed, even if not necessary. This
        // is useful for low frequency updates where sync behavior simplifies the
        // logic.
        // For high frequency updates (e.g. `resize` and `scroll` events), always
        // prefer the async Popper#update method
        forceUpdate: function forceUpdate() {
          if (isDestroyed) {
            return;
          }

          var _state$elements = state.elements,
              reference = _state$elements.reference,
              popper = _state$elements.popper; // Don't proceed if `reference` or `popper` are not valid elements
          // anymore

          if (!areValidElements(reference, popper)) {
            return;
          } // Store the reference and popper rects to be read by modifiers


          state.rects = {
            reference: getCompositeRect(reference, getOffsetParent(popper), state.options.strategy === 'fixed'),
            popper: getLayoutRect(popper)
          }; // Modifiers have the ability to reset the current update cycle. The
          // most common use case for this is the `flip` modifier changing the
          // placement, which then needs to re-run all the modifiers, because the
          // logic was previously ran for the previous placement and is therefore
          // stale/incorrect

          state.reset = false;
          state.placement = state.options.placement; // On each update cycle, the `modifiersData` property for each modifier
          // is filled with the initial data specified by the modifier. This means
          // it doesn't persist and is fresh on each update.
          // To ensure persistent data, use `${name}#persistent`

          state.orderedModifiers.forEach(function (modifier) {
            return state.modifiersData[modifier.name] = Object.assign({}, modifier.data);
          });

          for (var index = 0; index < state.orderedModifiers.length; index++) {
            if (state.reset === true) {
              state.reset = false;
              index = -1;
              continue;
            }

            var _state$orderedModifie = state.orderedModifiers[index],
                fn = _state$orderedModifie.fn,
                _state$orderedModifie2 = _state$orderedModifie.options,
                _options = _state$orderedModifie2 === void 0 ? {} : _state$orderedModifie2,
                name = _state$orderedModifie.name;

            if (typeof fn === 'function') {
              state = fn({
                state: state,
                options: _options,
                name: name,
                instance: instance
              }) || state;
            }
          }
        },
        // Async and optimistically optimized update – it will not be executed if
        // not necessary (debounced to run at most once-per-tick)
        update: debounce(function () {
          return new Promise(function (resolve) {
            instance.forceUpdate();
            resolve(state);
          });
        }),
        destroy: function destroy() {
          cleanupModifierEffects();
          isDestroyed = true;
        }
      };

      if (!areValidElements(reference, popper)) {
        return instance;
      }

      instance.setOptions(options).then(function (state) {
        if (!isDestroyed && options.onFirstUpdate) {
          options.onFirstUpdate(state);
        }
      }); // Modifiers have the ability to execute arbitrary code before the first
      // update cycle runs. They will be executed in the same order as the update
      // cycle. This is useful when a modifier adds some persistent data that
      // other modifiers need to use, but the modifier is run after the dependent
      // one.

      function runModifierEffects() {
        state.orderedModifiers.forEach(function (_ref) {
          var name = _ref.name,
              _ref$options = _ref.options,
              options = _ref$options === void 0 ? {} : _ref$options,
              effect = _ref.effect;

          if (typeof effect === 'function') {
            var cleanupFn = effect({
              state: state,
              name: name,
              instance: instance,
              options: options
            });

            var noopFn = function noopFn() {};

            effectCleanupFns.push(cleanupFn || noopFn);
          }
        });
      }

      function cleanupModifierEffects() {
        effectCleanupFns.forEach(function (fn) {
          return fn();
        });
        effectCleanupFns = [];
      }

      return instance;
    };
  }

  var passive = {
    passive: true
  };

  function effect$2(_ref) {
    var state = _ref.state,
        instance = _ref.instance,
        options = _ref.options;
    var _options$scroll = options.scroll,
        scroll = _options$scroll === void 0 ? true : _options$scroll,
        _options$resize = options.resize,
        resize = _options$resize === void 0 ? true : _options$resize;
    var window = getWindow(state.elements.popper);
    var scrollParents = [].concat(state.scrollParents.reference, state.scrollParents.popper);

    if (scroll) {
      scrollParents.forEach(function (scrollParent) {
        scrollParent.addEventListener('scroll', instance.update, passive);
      });
    }

    if (resize) {
      window.addEventListener('resize', instance.update, passive);
    }

    return function () {
      if (scroll) {
        scrollParents.forEach(function (scrollParent) {
          scrollParent.removeEventListener('scroll', instance.update, passive);
        });
      }

      if (resize) {
        window.removeEventListener('resize', instance.update, passive);
      }
    };
  } // eslint-disable-next-line import/no-unused-modules


  var eventListeners = {
    name: 'eventListeners',
    enabled: true,
    phase: 'write',
    fn: function fn() {},
    effect: effect$2,
    data: {}
  };

  function popperOffsets(_ref) {
    var state = _ref.state,
        name = _ref.name;
    // Offsets are the actual position the popper needs to have to be
    // properly positioned near its reference element
    // This is the most basic placement, and will be adjusted by
    // the modifiers in the next step
    state.modifiersData[name] = computeOffsets({
      reference: state.rects.reference,
      element: state.rects.popper,
      strategy: 'absolute',
      placement: state.placement
    });
  } // eslint-disable-next-line import/no-unused-modules


  var popperOffsets$1 = {
    name: 'popperOffsets',
    enabled: true,
    phase: 'read',
    fn: popperOffsets,
    data: {}
  };

  var unsetSides = {
    top: 'auto',
    right: 'auto',
    bottom: 'auto',
    left: 'auto'
  }; // Round the offsets to the nearest suitable subpixel based on the DPR.
  // Zooming can change the DPR, but it seems to report a value that will
  // cleanly divide the values into the appropriate subpixels.

  function roundOffsetsByDPR(_ref, win) {
    var x = _ref.x,
        y = _ref.y;
    var dpr = win.devicePixelRatio || 1;
    return {
      x: round(x * dpr) / dpr || 0,
      y: round(y * dpr) / dpr || 0
    };
  }

  function mapToStyles(_ref2) {
    var _Object$assign2;

    var popper = _ref2.popper,
        popperRect = _ref2.popperRect,
        placement = _ref2.placement,
        variation = _ref2.variation,
        offsets = _ref2.offsets,
        position = _ref2.position,
        gpuAcceleration = _ref2.gpuAcceleration,
        adaptive = _ref2.adaptive,
        roundOffsets = _ref2.roundOffsets,
        isFixed = _ref2.isFixed;
    var _offsets$x = offsets.x,
        x = _offsets$x === void 0 ? 0 : _offsets$x,
        _offsets$y = offsets.y,
        y = _offsets$y === void 0 ? 0 : _offsets$y;

    var _ref3 = typeof roundOffsets === 'function' ? roundOffsets({
      x: x,
      y: y
    }) : {
      x: x,
      y: y
    };

    x = _ref3.x;
    y = _ref3.y;
    var hasX = offsets.hasOwnProperty('x');
    var hasY = offsets.hasOwnProperty('y');
    var sideX = left;
    var sideY = top;
    var win = window;

    if (adaptive) {
      var offsetParent = getOffsetParent(popper);
      var heightProp = 'clientHeight';
      var widthProp = 'clientWidth';

      if (offsetParent === getWindow(popper)) {
        offsetParent = getDocumentElement(popper);

        if (getComputedStyle(offsetParent).position !== 'static' && position === 'absolute') {
          heightProp = 'scrollHeight';
          widthProp = 'scrollWidth';
        }
      } // $FlowFixMe[incompatible-cast]: force type refinement, we compare offsetParent with window above, but Flow doesn't detect it


      offsetParent = offsetParent;

      if (placement === top || (placement === left || placement === right) && variation === end) {
        sideY = bottom;
        var offsetY = isFixed && offsetParent === win && win.visualViewport ? win.visualViewport.height : // $FlowFixMe[prop-missing]
        offsetParent[heightProp];
        y -= offsetY - popperRect.height;
        y *= gpuAcceleration ? 1 : -1;
      }

      if (placement === left || (placement === top || placement === bottom) && variation === end) {
        sideX = right;
        var offsetX = isFixed && offsetParent === win && win.visualViewport ? win.visualViewport.width : // $FlowFixMe[prop-missing]
        offsetParent[widthProp];
        x -= offsetX - popperRect.width;
        x *= gpuAcceleration ? 1 : -1;
      }
    }

    var commonStyles = Object.assign({
      position: position
    }, adaptive && unsetSides);

    var _ref4 = roundOffsets === true ? roundOffsetsByDPR({
      x: x,
      y: y
    }, getWindow(popper)) : {
      x: x,
      y: y
    };

    x = _ref4.x;
    y = _ref4.y;

    if (gpuAcceleration) {
      var _Object$assign;

      return Object.assign({}, commonStyles, (_Object$assign = {}, _Object$assign[sideY] = hasY ? '0' : '', _Object$assign[sideX] = hasX ? '0' : '', _Object$assign.transform = (win.devicePixelRatio || 1) <= 1 ? "translate(" + x + "px, " + y + "px)" : "translate3d(" + x + "px, " + y + "px, 0)", _Object$assign));
    }

    return Object.assign({}, commonStyles, (_Object$assign2 = {}, _Object$assign2[sideY] = hasY ? y + "px" : '', _Object$assign2[sideX] = hasX ? x + "px" : '', _Object$assign2.transform = '', _Object$assign2));
  }

  function computeStyles(_ref5) {
    var state = _ref5.state,
        options = _ref5.options;
    var _options$gpuAccelerat = options.gpuAcceleration,
        gpuAcceleration = _options$gpuAccelerat === void 0 ? true : _options$gpuAccelerat,
        _options$adaptive = options.adaptive,
        adaptive = _options$adaptive === void 0 ? true : _options$adaptive,
        _options$roundOffsets = options.roundOffsets,
        roundOffsets = _options$roundOffsets === void 0 ? true : _options$roundOffsets;
    var commonStyles = {
      placement: getBasePlacement(state.placement),
      variation: getVariation(state.placement),
      popper: state.elements.popper,
      popperRect: state.rects.popper,
      gpuAcceleration: gpuAcceleration,
      isFixed: state.options.strategy === 'fixed'
    };

    if (state.modifiersData.popperOffsets != null) {
      state.styles.popper = Object.assign({}, state.styles.popper, mapToStyles(Object.assign({}, commonStyles, {
        offsets: state.modifiersData.popperOffsets,
        position: state.options.strategy,
        adaptive: adaptive,
        roundOffsets: roundOffsets
      })));
    }

    if (state.modifiersData.arrow != null) {
      state.styles.arrow = Object.assign({}, state.styles.arrow, mapToStyles(Object.assign({}, commonStyles, {
        offsets: state.modifiersData.arrow,
        position: 'absolute',
        adaptive: false,
        roundOffsets: roundOffsets
      })));
    }

    state.attributes.popper = Object.assign({}, state.attributes.popper, {
      'data-popper-placement': state.placement
    });
  } // eslint-disable-next-line import/no-unused-modules


  var computeStyles$1 = {
    name: 'computeStyles',
    enabled: true,
    phase: 'beforeWrite',
    fn: computeStyles,
    data: {}
  };

  // and applies them to the HTMLElements such as popper and arrow

  function applyStyles(_ref) {
    var state = _ref.state;
    Object.keys(state.elements).forEach(function (name) {
      var style = state.styles[name] || {};
      var attributes = state.attributes[name] || {};
      var element = state.elements[name]; // arrow is optional + virtual elements

      if (!isHTMLElement(element) || !getNodeName(element)) {
        return;
      } // Flow doesn't support to extend this property, but it's the most
      // effective way to apply styles to an HTMLElement
      // $FlowFixMe[cannot-write]


      Object.assign(element.style, style);
      Object.keys(attributes).forEach(function (name) {
        var value = attributes[name];

        if (value === false) {
          element.removeAttribute(name);
        } else {
          element.setAttribute(name, value === true ? '' : value);
        }
      });
    });
  }

  function effect$1(_ref2) {
    var state = _ref2.state;
    var initialStyles = {
      popper: {
        position: state.options.strategy,
        left: '0',
        top: '0',
        margin: '0'
      },
      arrow: {
        position: 'absolute'
      },
      reference: {}
    };
    Object.assign(state.elements.popper.style, initialStyles.popper);
    state.styles = initialStyles;

    if (state.elements.arrow) {
      Object.assign(state.elements.arrow.style, initialStyles.arrow);
    }

    return function () {
      Object.keys(state.elements).forEach(function (name) {
        var element = state.elements[name];
        var attributes = state.attributes[name] || {};
        var styleProperties = Object.keys(state.styles.hasOwnProperty(name) ? state.styles[name] : initialStyles[name]); // Set all values to an empty string to unset them

        var style = styleProperties.reduce(function (style, property) {
          style[property] = '';
          return style;
        }, {}); // arrow is optional + virtual elements

        if (!isHTMLElement(element) || !getNodeName(element)) {
          return;
        }

        Object.assign(element.style, style);
        Object.keys(attributes).forEach(function (attribute) {
          element.removeAttribute(attribute);
        });
      });
    };
  } // eslint-disable-next-line import/no-unused-modules


  var applyStyles$1 = {
    name: 'applyStyles',
    enabled: true,
    phase: 'write',
    fn: applyStyles,
    effect: effect$1,
    requires: ['computeStyles']
  };

  function distanceAndSkiddingToXY(placement, rects, offset) {
    var basePlacement = getBasePlacement(placement);
    var invertDistance = [left, top].indexOf(basePlacement) >= 0 ? -1 : 1;

    var _ref = typeof offset === 'function' ? offset(Object.assign({}, rects, {
      placement: placement
    })) : offset,
        skidding = _ref[0],
        distance = _ref[1];

    skidding = skidding || 0;
    distance = (distance || 0) * invertDistance;
    return [left, right].indexOf(basePlacement) >= 0 ? {
      x: distance,
      y: skidding
    } : {
      x: skidding,
      y: distance
    };
  }

  function offset(_ref2) {
    var state = _ref2.state,
        options = _ref2.options,
        name = _ref2.name;
    var _options$offset = options.offset,
        offset = _options$offset === void 0 ? [0, 0] : _options$offset;
    var data = placements.reduce(function (acc, placement) {
      acc[placement] = distanceAndSkiddingToXY(placement, state.rects, offset);
      return acc;
    }, {});
    var _data$state$placement = data[state.placement],
        x = _data$state$placement.x,
        y = _data$state$placement.y;

    if (state.modifiersData.popperOffsets != null) {
      state.modifiersData.popperOffsets.x += x;
      state.modifiersData.popperOffsets.y += y;
    }

    state.modifiersData[name] = data;
  } // eslint-disable-next-line import/no-unused-modules


  var offset$1 = {
    name: 'offset',
    enabled: true,
    phase: 'main',
    requires: ['popperOffsets'],
    fn: offset
  };

  var hash$1 = {
    left: 'right',
    right: 'left',
    bottom: 'top',
    top: 'bottom'
  };
  function getOppositePlacement(placement) {
    return placement.replace(/left|right|bottom|top/g, function (matched) {
      return hash$1[matched];
    });
  }

  var hash = {
    start: 'end',
    end: 'start'
  };
  function getOppositeVariationPlacement(placement) {
    return placement.replace(/start|end/g, function (matched) {
      return hash[matched];
    });
  }

  function computeAutoPlacement(state, options) {
    if (options === void 0) {
      options = {};
    }

    var _options = options,
        placement = _options.placement,
        boundary = _options.boundary,
        rootBoundary = _options.rootBoundary,
        padding = _options.padding,
        flipVariations = _options.flipVariations,
        _options$allowedAutoP = _options.allowedAutoPlacements,
        allowedAutoPlacements = _options$allowedAutoP === void 0 ? placements : _options$allowedAutoP;
    var variation = getVariation(placement);
    var placements$1 = variation ? flipVariations ? variationPlacements : variationPlacements.filter(function (placement) {
      return getVariation(placement) === variation;
    }) : basePlacements;
    var allowedPlacements = placements$1.filter(function (placement) {
      return allowedAutoPlacements.indexOf(placement) >= 0;
    });

    if (allowedPlacements.length === 0) {
      allowedPlacements = placements$1;
    } // $FlowFixMe[incompatible-type]: Flow seems to have problems with two array unions...


    var overflows = allowedPlacements.reduce(function (acc, placement) {
      acc[placement] = detectOverflow(state, {
        placement: placement,
        boundary: boundary,
        rootBoundary: rootBoundary,
        padding: padding
      })[getBasePlacement(placement)];
      return acc;
    }, {});
    return Object.keys(overflows).sort(function (a, b) {
      return overflows[a] - overflows[b];
    });
  }

  function getExpandedFallbackPlacements(placement) {
    if (getBasePlacement(placement) === auto) {
      return [];
    }

    var oppositePlacement = getOppositePlacement(placement);
    return [getOppositeVariationPlacement(placement), oppositePlacement, getOppositeVariationPlacement(oppositePlacement)];
  }

  function flip(_ref) {
    var state = _ref.state,
        options = _ref.options,
        name = _ref.name;

    if (state.modifiersData[name]._skip) {
      return;
    }

    var _options$mainAxis = options.mainAxis,
        checkMainAxis = _options$mainAxis === void 0 ? true : _options$mainAxis,
        _options$altAxis = options.altAxis,
        checkAltAxis = _options$altAxis === void 0 ? true : _options$altAxis,
        specifiedFallbackPlacements = options.fallbackPlacements,
        padding = options.padding,
        boundary = options.boundary,
        rootBoundary = options.rootBoundary,
        altBoundary = options.altBoundary,
        _options$flipVariatio = options.flipVariations,
        flipVariations = _options$flipVariatio === void 0 ? true : _options$flipVariatio,
        allowedAutoPlacements = options.allowedAutoPlacements;
    var preferredPlacement = state.options.placement;
    var basePlacement = getBasePlacement(preferredPlacement);
    var isBasePlacement = basePlacement === preferredPlacement;
    var fallbackPlacements = specifiedFallbackPlacements || (isBasePlacement || !flipVariations ? [getOppositePlacement(preferredPlacement)] : getExpandedFallbackPlacements(preferredPlacement));
    var placements = [preferredPlacement].concat(fallbackPlacements).reduce(function (acc, placement) {
      return acc.concat(getBasePlacement(placement) === auto ? computeAutoPlacement(state, {
        placement: placement,
        boundary: boundary,
        rootBoundary: rootBoundary,
        padding: padding,
        flipVariations: flipVariations,
        allowedAutoPlacements: allowedAutoPlacements
      }) : placement);
    }, []);
    var referenceRect = state.rects.reference;
    var popperRect = state.rects.popper;
    var checksMap = new Map();
    var makeFallbackChecks = true;
    var firstFittingPlacement = placements[0];

    for (var i = 0; i < placements.length; i++) {
      var placement = placements[i];

      var _basePlacement = getBasePlacement(placement);

      var isStartVariation = getVariation(placement) === start;
      var isVertical = [top, bottom].indexOf(_basePlacement) >= 0;
      var len = isVertical ? 'width' : 'height';
      var overflow = detectOverflow(state, {
        placement: placement,
        boundary: boundary,
        rootBoundary: rootBoundary,
        altBoundary: altBoundary,
        padding: padding
      });
      var mainVariationSide = isVertical ? isStartVariation ? right : left : isStartVariation ? bottom : top;

      if (referenceRect[len] > popperRect[len]) {
        mainVariationSide = getOppositePlacement(mainVariationSide);
      }

      var altVariationSide = getOppositePlacement(mainVariationSide);
      var checks = [];

      if (checkMainAxis) {
        checks.push(overflow[_basePlacement] <= 0);
      }

      if (checkAltAxis) {
        checks.push(overflow[mainVariationSide] <= 0, overflow[altVariationSide] <= 0);
      }

      if (checks.every(function (check) {
        return check;
      })) {
        firstFittingPlacement = placement;
        makeFallbackChecks = false;
        break;
      }

      checksMap.set(placement, checks);
    }

    if (makeFallbackChecks) {
      // `2` may be desired in some cases – research later
      var numberOfChecks = flipVariations ? 3 : 1;

      var _loop = function _loop(_i) {
        var fittingPlacement = placements.find(function (placement) {
          var checks = checksMap.get(placement);

          if (checks) {
            return checks.slice(0, _i).every(function (check) {
              return check;
            });
          }
        });

        if (fittingPlacement) {
          firstFittingPlacement = fittingPlacement;
          return "break";
        }
      };

      for (var _i = numberOfChecks; _i > 0; _i--) {
        var _ret = _loop(_i);

        if (_ret === "break") break;
      }
    }

    if (state.placement !== firstFittingPlacement) {
      state.modifiersData[name]._skip = true;
      state.placement = firstFittingPlacement;
      state.reset = true;
    }
  } // eslint-disable-next-line import/no-unused-modules


  var flip$1 = {
    name: 'flip',
    enabled: true,
    phase: 'main',
    fn: flip,
    requiresIfExists: ['offset'],
    data: {
      _skip: false
    }
  };

  function getAltAxis(axis) {
    return axis === 'x' ? 'y' : 'x';
  }

  function within(min$1, value, max$1) {
    return max(min$1, min(value, max$1));
  }
  function withinMaxClamp(min, value, max) {
    var v = within(min, value, max);
    return v > max ? max : v;
  }

  function preventOverflow(_ref) {
    var state = _ref.state,
        options = _ref.options,
        name = _ref.name;
    var _options$mainAxis = options.mainAxis,
        checkMainAxis = _options$mainAxis === void 0 ? true : _options$mainAxis,
        _options$altAxis = options.altAxis,
        checkAltAxis = _options$altAxis === void 0 ? false : _options$altAxis,
        boundary = options.boundary,
        rootBoundary = options.rootBoundary,
        altBoundary = options.altBoundary,
        padding = options.padding,
        _options$tether = options.tether,
        tether = _options$tether === void 0 ? true : _options$tether,
        _options$tetherOffset = options.tetherOffset,
        tetherOffset = _options$tetherOffset === void 0 ? 0 : _options$tetherOffset;
    var overflow = detectOverflow(state, {
      boundary: boundary,
      rootBoundary: rootBoundary,
      padding: padding,
      altBoundary: altBoundary
    });
    var basePlacement = getBasePlacement(state.placement);
    var variation = getVariation(state.placement);
    var isBasePlacement = !variation;
    var mainAxis = getMainAxisFromPlacement(basePlacement);
    var altAxis = getAltAxis(mainAxis);
    var popperOffsets = state.modifiersData.popperOffsets;
    var referenceRect = state.rects.reference;
    var popperRect = state.rects.popper;
    var tetherOffsetValue = typeof tetherOffset === 'function' ? tetherOffset(Object.assign({}, state.rects, {
      placement: state.placement
    })) : tetherOffset;
    var normalizedTetherOffsetValue = typeof tetherOffsetValue === 'number' ? {
      mainAxis: tetherOffsetValue,
      altAxis: tetherOffsetValue
    } : Object.assign({
      mainAxis: 0,
      altAxis: 0
    }, tetherOffsetValue);
    var offsetModifierState = state.modifiersData.offset ? state.modifiersData.offset[state.placement] : null;
    var data = {
      x: 0,
      y: 0
    };

    if (!popperOffsets) {
      return;
    }

    if (checkMainAxis) {
      var _offsetModifierState$;

      var mainSide = mainAxis === 'y' ? top : left;
      var altSide = mainAxis === 'y' ? bottom : right;
      var len = mainAxis === 'y' ? 'height' : 'width';
      var offset = popperOffsets[mainAxis];
      var min$1 = offset + overflow[mainSide];
      var max$1 = offset - overflow[altSide];
      var additive = tether ? -popperRect[len] / 2 : 0;
      var minLen = variation === start ? referenceRect[len] : popperRect[len];
      var maxLen = variation === start ? -popperRect[len] : -referenceRect[len]; // We need to include the arrow in the calculation so the arrow doesn't go
      // outside the reference bounds

      var arrowElement = state.elements.arrow;
      var arrowRect = tether && arrowElement ? getLayoutRect(arrowElement) : {
        width: 0,
        height: 0
      };
      var arrowPaddingObject = state.modifiersData['arrow#persistent'] ? state.modifiersData['arrow#persistent'].padding : getFreshSideObject();
      var arrowPaddingMin = arrowPaddingObject[mainSide];
      var arrowPaddingMax = arrowPaddingObject[altSide]; // If the reference length is smaller than the arrow length, we don't want
      // to include its full size in the calculation. If the reference is small
      // and near the edge of a boundary, the popper can overflow even if the
      // reference is not overflowing as well (e.g. virtual elements with no
      // width or height)

      var arrowLen = within(0, referenceRect[len], arrowRect[len]);
      var minOffset = isBasePlacement ? referenceRect[len] / 2 - additive - arrowLen - arrowPaddingMin - normalizedTetherOffsetValue.mainAxis : minLen - arrowLen - arrowPaddingMin - normalizedTetherOffsetValue.mainAxis;
      var maxOffset = isBasePlacement ? -referenceRect[len] / 2 + additive + arrowLen + arrowPaddingMax + normalizedTetherOffsetValue.mainAxis : maxLen + arrowLen + arrowPaddingMax + normalizedTetherOffsetValue.mainAxis;
      var arrowOffsetParent = state.elements.arrow && getOffsetParent(state.elements.arrow);
      var clientOffset = arrowOffsetParent ? mainAxis === 'y' ? arrowOffsetParent.clientTop || 0 : arrowOffsetParent.clientLeft || 0 : 0;
      var offsetModifierValue = (_offsetModifierState$ = offsetModifierState == null ? void 0 : offsetModifierState[mainAxis]) != null ? _offsetModifierState$ : 0;
      var tetherMin = offset + minOffset - offsetModifierValue - clientOffset;
      var tetherMax = offset + maxOffset - offsetModifierValue;
      var preventedOffset = within(tether ? min(min$1, tetherMin) : min$1, offset, tether ? max(max$1, tetherMax) : max$1);
      popperOffsets[mainAxis] = preventedOffset;
      data[mainAxis] = preventedOffset - offset;
    }

    if (checkAltAxis) {
      var _offsetModifierState$2;

      var _mainSide = mainAxis === 'x' ? top : left;

      var _altSide = mainAxis === 'x' ? bottom : right;

      var _offset = popperOffsets[altAxis];

      var _len = altAxis === 'y' ? 'height' : 'width';

      var _min = _offset + overflow[_mainSide];

      var _max = _offset - overflow[_altSide];

      var isOriginSide = [top, left].indexOf(basePlacement) !== -1;

      var _offsetModifierValue = (_offsetModifierState$2 = offsetModifierState == null ? void 0 : offsetModifierState[altAxis]) != null ? _offsetModifierState$2 : 0;

      var _tetherMin = isOriginSide ? _min : _offset - referenceRect[_len] - popperRect[_len] - _offsetModifierValue + normalizedTetherOffsetValue.altAxis;

      var _tetherMax = isOriginSide ? _offset + referenceRect[_len] + popperRect[_len] - _offsetModifierValue - normalizedTetherOffsetValue.altAxis : _max;

      var _preventedOffset = tether && isOriginSide ? withinMaxClamp(_tetherMin, _offset, _tetherMax) : within(tether ? _tetherMin : _min, _offset, tether ? _tetherMax : _max);

      popperOffsets[altAxis] = _preventedOffset;
      data[altAxis] = _preventedOffset - _offset;
    }

    state.modifiersData[name] = data;
  } // eslint-disable-next-line import/no-unused-modules


  var preventOverflow$1 = {
    name: 'preventOverflow',
    enabled: true,
    phase: 'main',
    fn: preventOverflow,
    requiresIfExists: ['offset']
  };

  var toPaddingObject = function toPaddingObject(padding, state) {
    padding = typeof padding === 'function' ? padding(Object.assign({}, state.rects, {
      placement: state.placement
    })) : padding;
    return mergePaddingObject(typeof padding !== 'number' ? padding : expandToHashMap(padding, basePlacements));
  };

  function arrow(_ref) {
    var _state$modifiersData$;

    var state = _ref.state,
        name = _ref.name,
        options = _ref.options;
    var arrowElement = state.elements.arrow;
    var popperOffsets = state.modifiersData.popperOffsets;
    var basePlacement = getBasePlacement(state.placement);
    var axis = getMainAxisFromPlacement(basePlacement);
    var isVertical = [left, right].indexOf(basePlacement) >= 0;
    var len = isVertical ? 'height' : 'width';

    if (!arrowElement || !popperOffsets) {
      return;
    }

    var paddingObject = toPaddingObject(options.padding, state);
    var arrowRect = getLayoutRect(arrowElement);
    var minProp = axis === 'y' ? top : left;
    var maxProp = axis === 'y' ? bottom : right;
    var endDiff = state.rects.reference[len] + state.rects.reference[axis] - popperOffsets[axis] - state.rects.popper[len];
    var startDiff = popperOffsets[axis] - state.rects.reference[axis];
    var arrowOffsetParent = getOffsetParent(arrowElement);
    var clientSize = arrowOffsetParent ? axis === 'y' ? arrowOffsetParent.clientHeight || 0 : arrowOffsetParent.clientWidth || 0 : 0;
    var centerToReference = endDiff / 2 - startDiff / 2; // Make sure the arrow doesn't overflow the popper if the center point is
    // outside of the popper bounds

    var min = paddingObject[minProp];
    var max = clientSize - arrowRect[len] - paddingObject[maxProp];
    var center = clientSize / 2 - arrowRect[len] / 2 + centerToReference;
    var offset = within(min, center, max); // Prevents breaking syntax highlighting...

    var axisProp = axis;
    state.modifiersData[name] = (_state$modifiersData$ = {}, _state$modifiersData$[axisProp] = offset, _state$modifiersData$.centerOffset = offset - center, _state$modifiersData$);
  }

  function effect(_ref2) {
    var state = _ref2.state,
        options = _ref2.options;
    var _options$element = options.element,
        arrowElement = _options$element === void 0 ? '[data-popper-arrow]' : _options$element;

    if (arrowElement == null) {
      return;
    } // CSS selector


    if (typeof arrowElement === 'string') {
      arrowElement = state.elements.popper.querySelector(arrowElement);

      if (!arrowElement) {
        return;
      }
    }

    if (!contains(state.elements.popper, arrowElement)) {
      return;
    }

    state.elements.arrow = arrowElement;
  } // eslint-disable-next-line import/no-unused-modules


  var arrow$1 = {
    name: 'arrow',
    enabled: true,
    phase: 'main',
    fn: arrow,
    effect: effect,
    requires: ['popperOffsets'],
    requiresIfExists: ['preventOverflow']
  };

  function getSideOffsets(overflow, rect, preventedOffsets) {
    if (preventedOffsets === void 0) {
      preventedOffsets = {
        x: 0,
        y: 0
      };
    }

    return {
      top: overflow.top - rect.height - preventedOffsets.y,
      right: overflow.right - rect.width + preventedOffsets.x,
      bottom: overflow.bottom - rect.height + preventedOffsets.y,
      left: overflow.left - rect.width - preventedOffsets.x
    };
  }

  function isAnySideFullyClipped(overflow) {
    return [top, right, bottom, left].some(function (side) {
      return overflow[side] >= 0;
    });
  }

  function hide(_ref) {
    var state = _ref.state,
        name = _ref.name;
    var referenceRect = state.rects.reference;
    var popperRect = state.rects.popper;
    var preventedOffsets = state.modifiersData.preventOverflow;
    var referenceOverflow = detectOverflow(state, {
      elementContext: 'reference'
    });
    var popperAltOverflow = detectOverflow(state, {
      altBoundary: true
    });
    var referenceClippingOffsets = getSideOffsets(referenceOverflow, referenceRect);
    var popperEscapeOffsets = getSideOffsets(popperAltOverflow, popperRect, preventedOffsets);
    var isReferenceHidden = isAnySideFullyClipped(referenceClippingOffsets);
    var hasPopperEscaped = isAnySideFullyClipped(popperEscapeOffsets);
    state.modifiersData[name] = {
      referenceClippingOffsets: referenceClippingOffsets,
      popperEscapeOffsets: popperEscapeOffsets,
      isReferenceHidden: isReferenceHidden,
      hasPopperEscaped: hasPopperEscaped
    };
    state.attributes.popper = Object.assign({}, state.attributes.popper, {
      'data-popper-reference-hidden': isReferenceHidden,
      'data-popper-escaped': hasPopperEscaped
    });
  } // eslint-disable-next-line import/no-unused-modules


  var hide$1 = {
    name: 'hide',
    enabled: true,
    phase: 'main',
    requiresIfExists: ['preventOverflow'],
    fn: hide
  };

  var defaultModifiers$1 = [eventListeners, popperOffsets$1, computeStyles$1, applyStyles$1];
  var createPopper$1 = /*#__PURE__*/popperGenerator({
    defaultModifiers: defaultModifiers$1
  }); // eslint-disable-next-line import/no-unused-modules

  var defaultModifiers = [eventListeners, popperOffsets$1, computeStyles$1, applyStyles$1, offset$1, flip$1, preventOverflow$1, arrow$1, hide$1];
  var createPopper = /*#__PURE__*/popperGenerator({
    defaultModifiers: defaultModifiers
  }); // eslint-disable-next-line import/no-unused-modules

  exports.applyStyles = applyStyles$1;
  exports.arrow = arrow$1;
  exports.computeStyles = computeStyles$1;
  exports.createPopper = createPopper;
  exports.createPopperLite = createPopper$1;
  exports.defaultModifiers = defaultModifiers;
  exports.detectOverflow = detectOverflow;
  exports.eventListeners = eventListeners;
  exports.flip = flip$1;
  exports.hide = hide$1;
  exports.offset = offset$1;
  exports.popperGenerator = popperGenerator;
  exports.popperOffsets = popperOffsets$1;
  exports.preventOverflow = preventOverflow$1;

  Object.defineProperty(exports, '__esModule', { value: true });

})));


/*!
  * Bootstrap v5.3.3 (https://getbootstrap.com/)
  * Copyright 2011-2024 The Bootstrap Authors (https://github.com/twbs/bootstrap/graphs/contributors)
  * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
  */
(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory(require('@popperjs/core')) :
  typeof define === 'function' && define.amd ? define(['@popperjs/core'], factory) :
  (global = typeof globalThis !== 'undefined' ? globalThis : global || self, global.bootstrap = factory(global.Popper));
})(this, (function (Popper) { 'use strict';

  function _interopNamespaceDefault(e) {
    const n = Object.create(null, { [Symbol.toStringTag]: { value: 'Module' } });
    if (e) {
      for (const k in e) {
        if (k !== 'default') {
          const d = Object.getOwnPropertyDescriptor(e, k);
          Object.defineProperty(n, k, d.get ? d : {
            enumerable: true,
            get: () => e[k]
          });
        }
      }
    }
    n.default = e;
    return Object.freeze(n);
  }

  const Popper__namespace = /*#__PURE__*/_interopNamespaceDefault(Popper);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap dom/data.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  /**
   * Constants
   */

  const elementMap = new Map();
  const Data = {
    set(element, key, instance) {
      if (!elementMap.has(element)) {
        elementMap.set(element, new Map());
      }
      const instanceMap = elementMap.get(element);

      // make it clear we only want one instance per element
      // can be removed later when multiple key/instances are fine to be used
      if (!instanceMap.has(key) && instanceMap.size !== 0) {
        // eslint-disable-next-line no-console
        console.error(`Bootstrap doesn't allow more than one instance per element. Bound instance: ${Array.from(instanceMap.keys())[0]}.`);
        return;
      }
      instanceMap.set(key, instance);
    },
    get(element, key) {
      if (elementMap.has(element)) {
        return elementMap.get(element).get(key) || null;
      }
      return null;
    },
    remove(element, key) {
      if (!elementMap.has(element)) {
        return;
      }
      const instanceMap = elementMap.get(element);
      instanceMap.delete(key);

      // free up element references if there are no instances left for an element
      if (instanceMap.size === 0) {
        elementMap.delete(element);
      }
    }
  };

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/index.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  const MAX_UID = 1000000;
  const MILLISECONDS_MULTIPLIER = 1000;
  const TRANSITION_END = 'transitionend';

  /**
   * Properly escape IDs selectors to handle weird IDs
   * @param {string} selector
   * @returns {string}
   */
  const parseSelector = selector => {
    if (selector && window.CSS && window.CSS.escape) {
      // document.querySelector needs escaping to handle IDs (html5+) containing for instance /
      selector = selector.replace(/#([^\s"#']+)/g, (match, id) => `#${CSS.escape(id)}`);
    }
    return selector;
  };

  // Shout-out Angus Croll (https://goo.gl/pxwQGp)
  const toType = object => {
    if (object === null || object === undefined) {
      return `${object}`;
    }
    return Object.prototype.toString.call(object).match(/\s([a-z]+)/i)[1].toLowerCase();
  };

  /**
   * Public Util API
   */

  const getUID = prefix => {
    do {
      prefix += Math.floor(Math.random() * MAX_UID);
    } while (document.getElementById(prefix));
    return prefix;
  };
  const getTransitionDurationFromElement = element => {
    if (!element) {
      return 0;
    }

    // Get transition-duration of the element
    let {
      transitionDuration,
      transitionDelay
    } = window.getComputedStyle(element);
    const floatTransitionDuration = Number.parseFloat(transitionDuration);
    const floatTransitionDelay = Number.parseFloat(transitionDelay);

    // Return 0 if element or transition duration is not found
    if (!floatTransitionDuration && !floatTransitionDelay) {
      return 0;
    }

    // If multiple durations are defined, take the first
    transitionDuration = transitionDuration.split(',')[0];
    transitionDelay = transitionDelay.split(',')[0];
    return (Number.parseFloat(transitionDuration) + Number.parseFloat(transitionDelay)) * MILLISECONDS_MULTIPLIER;
  };
  const triggerTransitionEnd = element => {
    element.dispatchEvent(new Event(TRANSITION_END));
  };
  const isElement = object => {
    if (!object || typeof object !== 'object') {
      return false;
    }
    if (typeof object.jquery !== 'undefined') {
      object = object[0];
    }
    return typeof object.nodeType !== 'undefined';
  };
  const getElement = object => {
    // it's a jQuery object or a node element
    if (isElement(object)) {
      return object.jquery ? object[0] : object;
    }
    if (typeof object === 'string' && object.length > 0) {
      return document.querySelector(parseSelector(object));
    }
    return null;
  };
  const isVisible = element => {
    if (!isElement(element) || element.getClientRects().length === 0) {
      return false;
    }
    const elementIsVisible = getComputedStyle(element).getPropertyValue('visibility') === 'visible';
    // Handle `details` element as its content may falsie appear visible when it is closed
    const closedDetails = element.closest('details:not([open])');
    if (!closedDetails) {
      return elementIsVisible;
    }
    if (closedDetails !== element) {
      const summary = element.closest('summary');
      if (summary && summary.parentNode !== closedDetails) {
        return false;
      }
      if (summary === null) {
        return false;
      }
    }
    return elementIsVisible;
  };
  const isDisabled = element => {
    if (!element || element.nodeType !== Node.ELEMENT_NODE) {
      return true;
    }
    if (element.classList.contains('disabled')) {
      return true;
    }
    if (typeof element.disabled !== 'undefined') {
      return element.disabled;
    }
    return element.hasAttribute('disabled') && element.getAttribute('disabled') !== 'false';
  };
  const findShadowRoot = element => {
    if (!document.documentElement.attachShadow) {
      return null;
    }

    // Can find the shadow root otherwise it'll return the document
    if (typeof element.getRootNode === 'function') {
      const root = element.getRootNode();
      return root instanceof ShadowRoot ? root : null;
    }
    if (element instanceof ShadowRoot) {
      return element;
    }

    // when we don't find a shadow root
    if (!element.parentNode) {
      return null;
    }
    return findShadowRoot(element.parentNode);
  };
  const noop = () => {};

  /**
   * Trick to restart an element's animation
   *
   * @param {HTMLElement} element
   * @return void
   *
   * @see https://www.charistheo.io/blog/2021/02/restart-a-css-animation-with-javascript/#restarting-a-css-animation
   */
  const reflow = element => {
    element.offsetHeight; // eslint-disable-line no-unused-expressions
  };
  const getjQuery = () => {
    if (window.jQuery && !document.body.hasAttribute('data-bs-no-jquery')) {
      return window.jQuery;
    }
    return null;
  };
  const DOMContentLoadedCallbacks = [];
  const onDOMContentLoaded = callback => {
    if (document.readyState === 'loading') {
      // add listener on the first call when the document is in loading state
      if (!DOMContentLoadedCallbacks.length) {
        document.addEventListener('DOMContentLoaded', () => {
          for (const callback of DOMContentLoadedCallbacks) {
            callback();
          }
        });
      }
      DOMContentLoadedCallbacks.push(callback);
    } else {
      callback();
    }
  };
  const isRTL = () => document.documentElement.dir === 'rtl';
  const defineJQueryPlugin = plugin => {
    onDOMContentLoaded(() => {
      const $ = getjQuery();
      /* istanbul ignore if */
      if ($) {
        const name = plugin.NAME;
        const JQUERY_NO_CONFLICT = $.fn[name];
        $.fn[name] = plugin.jQueryInterface;
        $.fn[name].Constructor = plugin;
        $.fn[name].noConflict = () => {
          $.fn[name] = JQUERY_NO_CONFLICT;
          return plugin.jQueryInterface;
        };
      }
    });
  };
  const execute = (possibleCallback, args = [], defaultValue = possibleCallback) => {
    return typeof possibleCallback === 'function' ? possibleCallback(...args) : defaultValue;
  };
  const executeAfterTransition = (callback, transitionElement, waitForTransition = true) => {
    if (!waitForTransition) {
      execute(callback);
      return;
    }
    const durationPadding = 5;
    const emulatedDuration = getTransitionDurationFromElement(transitionElement) + durationPadding;
    let called = false;
    const handler = ({
      target
    }) => {
      if (target !== transitionElement) {
        return;
      }
      called = true;
      transitionElement.removeEventListener(TRANSITION_END, handler);
      execute(callback);
    };
    transitionElement.addEventListener(TRANSITION_END, handler);
    setTimeout(() => {
      if (!called) {
        triggerTransitionEnd(transitionElement);
      }
    }, emulatedDuration);
  };

  /**
   * Return the previous/next element of a list.
   *
   * @param {array} list    The list of elements
   * @param activeElement   The active element
   * @param shouldGetNext   Choose to get next or previous element
   * @param isCycleAllowed
   * @return {Element|elem} The proper element
   */
  const getNextActiveElement = (list, activeElement, shouldGetNext, isCycleAllowed) => {
    const listLength = list.length;
    let index = list.indexOf(activeElement);

    // if the element does not exist in the list return an element
    // depending on the direction and if cycle is allowed
    if (index === -1) {
      return !shouldGetNext && isCycleAllowed ? list[listLength - 1] : list[0];
    }
    index += shouldGetNext ? 1 : -1;
    if (isCycleAllowed) {
      index = (index + listLength) % listLength;
    }
    return list[Math.max(0, Math.min(index, listLength - 1))];
  };

  /**
   * --------------------------------------------------------------------------
   * Bootstrap dom/event-handler.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const namespaceRegex = /[^.]*(?=\..*)\.|.*/;
  const stripNameRegex = /\..*/;
  const stripUidRegex = /::\d+$/;
  const eventRegistry = {}; // Events storage
  let uidEvent = 1;
  const customEvents = {
    mouseenter: 'mouseover',
    mouseleave: 'mouseout'
  };
  const nativeEvents = new Set(['click', 'dblclick', 'mouseup', 'mousedown', 'contextmenu', 'mousewheel', 'DOMMouseScroll', 'mouseover', 'mouseout', 'mousemove', 'selectstart', 'selectend', 'keydown', 'keypress', 'keyup', 'orientationchange', 'touchstart', 'touchmove', 'touchend', 'touchcancel', 'pointerdown', 'pointermove', 'pointerup', 'pointerleave', 'pointercancel', 'gesturestart', 'gesturechange', 'gestureend', 'focus', 'blur', 'change', 'reset', 'select', 'submit', 'focusin', 'focusout', 'load', 'unload', 'beforeunload', 'resize', 'move', 'DOMContentLoaded', 'readystatechange', 'error', 'abort', 'scroll']);

  /**
   * Private methods
   */

  function makeEventUid(element, uid) {
    return uid && `${uid}::${uidEvent++}` || element.uidEvent || uidEvent++;
  }
  function getElementEvents(element) {
    const uid = makeEventUid(element);
    element.uidEvent = uid;
    eventRegistry[uid] = eventRegistry[uid] || {};
    return eventRegistry[uid];
  }
  function bootstrapHandler(element, fn) {
    return function handler(event) {
      hydrateObj(event, {
        delegateTarget: element
      });
      if (handler.oneOff) {
        EventHandler.off(element, event.type, fn);
      }
      return fn.apply(element, [event]);
    };
  }
  function bootstrapDelegationHandler(element, selector, fn) {
    return function handler(event) {
      const domElements = element.querySelectorAll(selector);
      for (let {
        target
      } = event; target && target !== this; target = target.parentNode) {
        for (const domElement of domElements) {
          if (domElement !== target) {
            continue;
          }
          hydrateObj(event, {
            delegateTarget: target
          });
          if (handler.oneOff) {
            EventHandler.off(element, event.type, selector, fn);
          }
          return fn.apply(target, [event]);
        }
      }
    };
  }
  function findHandler(events, callable, delegationSelector = null) {
    return Object.values(events).find(event => event.callable === callable && event.delegationSelector === delegationSelector);
  }
  function normalizeParameters(originalTypeEvent, handler, delegationFunction) {
    const isDelegated = typeof handler === 'string';
    // TODO: tooltip passes `false` instead of selector, so we need to check
    const callable = isDelegated ? delegationFunction : handler || delegationFunction;
    let typeEvent = getTypeEvent(originalTypeEvent);
    if (!nativeEvents.has(typeEvent)) {
      typeEvent = originalTypeEvent;
    }
    return [isDelegated, callable, typeEvent];
  }
  function addHandler(element, originalTypeEvent, handler, delegationFunction, oneOff) {
    if (typeof originalTypeEvent !== 'string' || !element) {
      return;
    }
    let [isDelegated, callable, typeEvent] = normalizeParameters(originalTypeEvent, handler, delegationFunction);

    // in case of mouseenter or mouseleave wrap the handler within a function that checks for its DOM position
    // this prevents the handler from being dispatched the same way as mouseover or mouseout does
    if (originalTypeEvent in customEvents) {
      const wrapFunction = fn => {
        return function (event) {
          if (!event.relatedTarget || event.relatedTarget !== event.delegateTarget && !event.delegateTarget.contains(event.relatedTarget)) {
            return fn.call(this, event);
          }
        };
      };
      callable = wrapFunction(callable);
    }
    const events = getElementEvents(element);
    const handlers = events[typeEvent] || (events[typeEvent] = {});
    const previousFunction = findHandler(handlers, callable, isDelegated ? handler : null);
    if (previousFunction) {
      previousFunction.oneOff = previousFunction.oneOff && oneOff;
      return;
    }
    const uid = makeEventUid(callable, originalTypeEvent.replace(namespaceRegex, ''));
    const fn = isDelegated ? bootstrapDelegationHandler(element, handler, callable) : bootstrapHandler(element, callable);
    fn.delegationSelector = isDelegated ? handler : null;
    fn.callable = callable;
    fn.oneOff = oneOff;
    fn.uidEvent = uid;
    handlers[uid] = fn;
    element.addEventListener(typeEvent, fn, isDelegated);
  }
  function removeHandler(element, events, typeEvent, handler, delegationSelector) {
    const fn = findHandler(events[typeEvent], handler, delegationSelector);
    if (!fn) {
      return;
    }
    element.removeEventListener(typeEvent, fn, Boolean(delegationSelector));
    delete events[typeEvent][fn.uidEvent];
  }
  function removeNamespacedHandlers(element, events, typeEvent, namespace) {
    const storeElementEvent = events[typeEvent] || {};
    for (const [handlerKey, event] of Object.entries(storeElementEvent)) {
      if (handlerKey.includes(namespace)) {
        removeHandler(element, events, typeEvent, event.callable, event.delegationSelector);
      }
    }
  }
  function getTypeEvent(event) {
    // allow to get the native events from namespaced events ('click.bs.button' --> 'click')
    event = event.replace(stripNameRegex, '');
    return customEvents[event] || event;
  }
  const EventHandler = {
    on(element, event, handler, delegationFunction) {
      addHandler(element, event, handler, delegationFunction, false);
    },
    one(element, event, handler, delegationFunction) {
      addHandler(element, event, handler, delegationFunction, true);
    },
    off(element, originalTypeEvent, handler, delegationFunction) {
      if (typeof originalTypeEvent !== 'string' || !element) {
        return;
      }
      const [isDelegated, callable, typeEvent] = normalizeParameters(originalTypeEvent, handler, delegationFunction);
      const inNamespace = typeEvent !== originalTypeEvent;
      const events = getElementEvents(element);
      const storeElementEvent = events[typeEvent] || {};
      const isNamespace = originalTypeEvent.startsWith('.');
      if (typeof callable !== 'undefined') {
        // Simplest case: handler is passed, remove that listener ONLY.
        if (!Object.keys(storeElementEvent).length) {
          return;
        }
        removeHandler(element, events, typeEvent, callable, isDelegated ? handler : null);
        return;
      }
      if (isNamespace) {
        for (const elementEvent of Object.keys(events)) {
          removeNamespacedHandlers(element, events, elementEvent, originalTypeEvent.slice(1));
        }
      }
      for (const [keyHandlers, event] of Object.entries(storeElementEvent)) {
        const handlerKey = keyHandlers.replace(stripUidRegex, '');
        if (!inNamespace || originalTypeEvent.includes(handlerKey)) {
          removeHandler(element, events, typeEvent, event.callable, event.delegationSelector);
        }
      }
    },
    trigger(element, event, args) {
      if (typeof event !== 'string' || !element) {
        return null;
      }
      const $ = getjQuery();
      const typeEvent = getTypeEvent(event);
      const inNamespace = event !== typeEvent;
      let jQueryEvent = null;
      let bubbles = true;
      let nativeDispatch = true;
      let defaultPrevented = false;
      if (inNamespace && $) {
        jQueryEvent = $.Event(event, args);
        $(element).trigger(jQueryEvent);
        bubbles = !jQueryEvent.isPropagationStopped();
        nativeDispatch = !jQueryEvent.isImmediatePropagationStopped();
        defaultPrevented = jQueryEvent.isDefaultPrevented();
      }
      const evt = hydrateObj(new Event(event, {
        bubbles,
        cancelable: true
      }), args);
      if (defaultPrevented) {
        evt.preventDefault();
      }
      if (nativeDispatch) {
        element.dispatchEvent(evt);
      }
      if (evt.defaultPrevented && jQueryEvent) {
        jQueryEvent.preventDefault();
      }
      return evt;
    }
  };
  function hydrateObj(obj, meta = {}) {
    for (const [key, value] of Object.entries(meta)) {
      try {
        obj[key] = value;
      } catch (_unused) {
        Object.defineProperty(obj, key, {
          configurable: true,
          get() {
            return value;
          }
        });
      }
    }
    return obj;
  }

  /**
   * --------------------------------------------------------------------------
   * Bootstrap dom/manipulator.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  function normalizeData(value) {
    if (value === 'true') {
      return true;
    }
    if (value === 'false') {
      return false;
    }
    if (value === Number(value).toString()) {
      return Number(value);
    }
    if (value === '' || value === 'null') {
      return null;
    }
    if (typeof value !== 'string') {
      return value;
    }
    try {
      return JSON.parse(decodeURIComponent(value));
    } catch (_unused) {
      return value;
    }
  }
  function normalizeDataKey(key) {
    return key.replace(/[A-Z]/g, chr => `-${chr.toLowerCase()}`);
  }
  const Manipulator = {
    setDataAttribute(element, key, value) {
      element.setAttribute(`data-bs-${normalizeDataKey(key)}`, value);
    },
    removeDataAttribute(element, key) {
      element.removeAttribute(`data-bs-${normalizeDataKey(key)}`);
    },
    getDataAttributes(element) {
      if (!element) {
        return {};
      }
      const attributes = {};
      const bsKeys = Object.keys(element.dataset).filter(key => key.startsWith('bs') && !key.startsWith('bsConfig'));
      for (const key of bsKeys) {
        let pureKey = key.replace(/^bs/, '');
        pureKey = pureKey.charAt(0).toLowerCase() + pureKey.slice(1, pureKey.length);
        attributes[pureKey] = normalizeData(element.dataset[key]);
      }
      return attributes;
    },
    getDataAttribute(element, key) {
      return normalizeData(element.getAttribute(`data-bs-${normalizeDataKey(key)}`));
    }
  };

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/config.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Class definition
   */

  class Config {
    // Getters
    static get Default() {
      return {};
    }
    static get DefaultType() {
      return {};
    }
    static get NAME() {
      throw new Error('You have to implement the static method "NAME", for each component!');
    }
    _getConfig(config) {
      config = this._mergeConfigObj(config);
      config = this._configAfterMerge(config);
      this._typeCheckConfig(config);
      return config;
    }
    _configAfterMerge(config) {
      return config;
    }
    _mergeConfigObj(config, element) {
      const jsonConfig = isElement(element) ? Manipulator.getDataAttribute(element, 'config') : {}; // try to parse

      return {
        ...this.constructor.Default,
        ...(typeof jsonConfig === 'object' ? jsonConfig : {}),
        ...(isElement(element) ? Manipulator.getDataAttributes(element) : {}),
        ...(typeof config === 'object' ? config : {})
      };
    }
    _typeCheckConfig(config, configTypes = this.constructor.DefaultType) {
      for (const [property, expectedTypes] of Object.entries(configTypes)) {
        const value = config[property];
        const valueType = isElement(value) ? 'element' : toType(value);
        if (!new RegExp(expectedTypes).test(valueType)) {
          throw new TypeError(`${this.constructor.NAME.toUpperCase()}: Option "${property}" provided type "${valueType}" but expected type "${expectedTypes}".`);
        }
      }
    }
  }

  /**
   * --------------------------------------------------------------------------
   * Bootstrap base-component.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const VERSION = '5.3.3';

  /**
   * Class definition
   */

  class BaseComponent extends Config {
    constructor(element, config) {
      super();
      element = getElement(element);
      if (!element) {
        return;
      }
      this._element = element;
      this._config = this._getConfig(config);
      Data.set(this._element, this.constructor.DATA_KEY, this);
    }

    // Public
    dispose() {
      Data.remove(this._element, this.constructor.DATA_KEY);
      EventHandler.off(this._element, this.constructor.EVENT_KEY);
      for (const propertyName of Object.getOwnPropertyNames(this)) {
        this[propertyName] = null;
      }
    }
    _queueCallback(callback, element, isAnimated = true) {
      executeAfterTransition(callback, element, isAnimated);
    }
    _getConfig(config) {
      config = this._mergeConfigObj(config, this._element);
      config = this._configAfterMerge(config);
      this._typeCheckConfig(config);
      return config;
    }

    // Static
    static getInstance(element) {
      return Data.get(getElement(element), this.DATA_KEY);
    }
    static getOrCreateInstance(element, config = {}) {
      return this.getInstance(element) || new this(element, typeof config === 'object' ? config : null);
    }
    static get VERSION() {
      return VERSION;
    }
    static get DATA_KEY() {
      return `bs.${this.NAME}`;
    }
    static get EVENT_KEY() {
      return `.${this.DATA_KEY}`;
    }
    static eventName(name) {
      return `${name}${this.EVENT_KEY}`;
    }
  }

  /**
   * --------------------------------------------------------------------------
   * Bootstrap dom/selector-engine.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  const getSelector = element => {
    let selector = element.getAttribute('data-bs-target');
    if (!selector || selector === '#') {
      let hrefAttribute = element.getAttribute('href');

      // The only valid content that could double as a selector are IDs or classes,
      // so everything starting with `#` or `.`. If a "real" URL is used as the selector,
      // `document.querySelector` will rightfully complain it is invalid.
      // See https://github.com/twbs/bootstrap/issues/32273
      if (!hrefAttribute || !hrefAttribute.includes('#') && !hrefAttribute.startsWith('.')) {
        return null;
      }

      // Just in case some CMS puts out a full URL with the anchor appended
      if (hrefAttribute.includes('#') && !hrefAttribute.startsWith('#')) {
        hrefAttribute = `#${hrefAttribute.split('#')[1]}`;
      }
      selector = hrefAttribute && hrefAttribute !== '#' ? hrefAttribute.trim() : null;
    }
    return selector ? selector.split(',').map(sel => parseSelector(sel)).join(',') : null;
  };
  const SelectorEngine = {
    find(selector, element = document.documentElement) {
      return [].concat(...Element.prototype.querySelectorAll.call(element, selector));
    },
    findOne(selector, element = document.documentElement) {
      return Element.prototype.querySelector.call(element, selector);
    },
    children(element, selector) {
      return [].concat(...element.children).filter(child => child.matches(selector));
    },
    parents(element, selector) {
      const parents = [];
      let ancestor = element.parentNode.closest(selector);
      while (ancestor) {
        parents.push(ancestor);
        ancestor = ancestor.parentNode.closest(selector);
      }
      return parents;
    },
    prev(element, selector) {
      let previous = element.previousElementSibling;
      while (previous) {
        if (previous.matches(selector)) {
          return [previous];
        }
        previous = previous.previousElementSibling;
      }
      return [];
    },
    // TODO: this is now unused; remove later along with prev()
    next(element, selector) {
      let next = element.nextElementSibling;
      while (next) {
        if (next.matches(selector)) {
          return [next];
        }
        next = next.nextElementSibling;
      }
      return [];
    },
    focusableChildren(element) {
      const focusables = ['a', 'button', 'input', 'textarea', 'select', 'details', '[tabindex]', '[contenteditable="true"]'].map(selector => `${selector}:not([tabindex^="-"])`).join(',');
      return this.find(focusables, element).filter(el => !isDisabled(el) && isVisible(el));
    },
    getSelectorFromElement(element) {
      const selector = getSelector(element);
      if (selector) {
        return SelectorEngine.findOne(selector) ? selector : null;
      }
      return null;
    },
    getElementFromSelector(element) {
      const selector = getSelector(element);
      return selector ? SelectorEngine.findOne(selector) : null;
    },
    getMultipleElementsFromSelector(element) {
      const selector = getSelector(element);
      return selector ? SelectorEngine.find(selector) : [];
    }
  };

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/component-functions.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  const enableDismissTrigger = (component, method = 'hide') => {
    const clickEvent = `click.dismiss${component.EVENT_KEY}`;
    const name = component.NAME;
    EventHandler.on(document, clickEvent, `[data-bs-dismiss="${name}"]`, function (event) {
      if (['A', 'AREA'].includes(this.tagName)) {
        event.preventDefault();
      }
      if (isDisabled(this)) {
        return;
      }
      const target = SelectorEngine.getElementFromSelector(this) || this.closest(`.${name}`);
      const instance = component.getOrCreateInstance(target);

      // Method argument is left, for Alert and only, as it doesn't implement the 'hide' method
      instance[method]();
    });
  };

  /**
   * --------------------------------------------------------------------------
   * Bootstrap alert.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$f = 'alert';
  const DATA_KEY$a = 'bs.alert';
  const EVENT_KEY$b = `.${DATA_KEY$a}`;
  const EVENT_CLOSE = `close${EVENT_KEY$b}`;
  const EVENT_CLOSED = `closed${EVENT_KEY$b}`;
  const CLASS_NAME_FADE$5 = 'fade';
  const CLASS_NAME_SHOW$8 = 'show';

  /**
   * Class definition
   */

  class Alert extends BaseComponent {
    // Getters
    static get NAME() {
      return NAME$f;
    }

    // Public
    close() {
      const closeEvent = EventHandler.trigger(this._element, EVENT_CLOSE);
      if (closeEvent.defaultPrevented) {
        return;
      }
      this._element.classList.remove(CLASS_NAME_SHOW$8);
      const isAnimated = this._element.classList.contains(CLASS_NAME_FADE$5);
      this._queueCallback(() => this._destroyElement(), this._element, isAnimated);
    }

    // Private
    _destroyElement() {
      this._element.remove();
      EventHandler.trigger(this._element, EVENT_CLOSED);
      this.dispose();
    }

    // Static
    static jQueryInterface(config) {
      return this.each(function () {
        const data = Alert.getOrCreateInstance(this);
        if (typeof config !== 'string') {
          return;
        }
        if (data[config] === undefined || config.startsWith('_') || config === 'constructor') {
          throw new TypeError(`No method named "${config}"`);
        }
        data[config](this);
      });
    }
  }

  /**
   * Data API implementation
   */

  enableDismissTrigger(Alert, 'close');

  /**
   * jQuery
   */

  defineJQueryPlugin(Alert);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap button.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$e = 'button';
  const DATA_KEY$9 = 'bs.button';
  const EVENT_KEY$a = `.${DATA_KEY$9}`;
  const DATA_API_KEY$6 = '.data-api';
  const CLASS_NAME_ACTIVE$3 = 'active';
  const SELECTOR_DATA_TOGGLE$5 = '[data-bs-toggle="button"]';
  const EVENT_CLICK_DATA_API$6 = `click${EVENT_KEY$a}${DATA_API_KEY$6}`;

  /**
   * Class definition
   */

  class Button extends BaseComponent {
    // Getters
    static get NAME() {
      return NAME$e;
    }

    // Public
    toggle() {
      // Toggle class and sync the `aria-pressed` attribute with the return value of the `.toggle()` method
      this._element.setAttribute('aria-pressed', this._element.classList.toggle(CLASS_NAME_ACTIVE$3));
    }

    // Static
    static jQueryInterface(config) {
      return this.each(function () {
        const data = Button.getOrCreateInstance(this);
        if (config === 'toggle') {
          data[config]();
        }
      });
    }
  }

  /**
   * Data API implementation
   */

  EventHandler.on(document, EVENT_CLICK_DATA_API$6, SELECTOR_DATA_TOGGLE$5, event => {
    event.preventDefault();
    const button = event.target.closest(SELECTOR_DATA_TOGGLE$5);
    const data = Button.getOrCreateInstance(button);
    data.toggle();
  });

  /**
   * jQuery
   */

  defineJQueryPlugin(Button);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/swipe.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$d = 'swipe';
  const EVENT_KEY$9 = '.bs.swipe';
  const EVENT_TOUCHSTART = `touchstart${EVENT_KEY$9}`;
  const EVENT_TOUCHMOVE = `touchmove${EVENT_KEY$9}`;
  const EVENT_TOUCHEND = `touchend${EVENT_KEY$9}`;
  const EVENT_POINTERDOWN = `pointerdown${EVENT_KEY$9}`;
  const EVENT_POINTERUP = `pointerup${EVENT_KEY$9}`;
  const POINTER_TYPE_TOUCH = 'touch';
  const POINTER_TYPE_PEN = 'pen';
  const CLASS_NAME_POINTER_EVENT = 'pointer-event';
  const SWIPE_THRESHOLD = 40;
  const Default$c = {
    endCallback: null,
    leftCallback: null,
    rightCallback: null
  };
  const DefaultType$c = {
    endCallback: '(function|null)',
    leftCallback: '(function|null)',
    rightCallback: '(function|null)'
  };

  /**
   * Class definition
   */

  class Swipe extends Config {
    constructor(element, config) {
      super();
      this._element = element;
      if (!element || !Swipe.isSupported()) {
        return;
      }
      this._config = this._getConfig(config);
      this._deltaX = 0;
      this._supportPointerEvents = Boolean(window.PointerEvent);
      this._initEvents();
    }

    // Getters
    static get Default() {
      return Default$c;
    }
    static get DefaultType() {
      return DefaultType$c;
    }
    static get NAME() {
      return NAME$d;
    }

    // Public
    dispose() {
      EventHandler.off(this._element, EVENT_KEY$9);
    }

    // Private
    _start(event) {
      if (!this._supportPointerEvents) {
        this._deltaX = event.touches[0].clientX;
        return;
      }
      if (this._eventIsPointerPenTouch(event)) {
        this._deltaX = event.clientX;
      }
    }
    _end(event) {
      if (this._eventIsPointerPenTouch(event)) {
        this._deltaX = event.clientX - this._deltaX;
      }
      this._handleSwipe();
      execute(this._config.endCallback);
    }
    _move(event) {
      this._deltaX = event.touches && event.touches.length > 1 ? 0 : event.touches[0].clientX - this._deltaX;
    }
    _handleSwipe() {
      const absDeltaX = Math.abs(this._deltaX);
      if (absDeltaX <= SWIPE_THRESHOLD) {
        return;
      }
      const direction = absDeltaX / this._deltaX;
      this._deltaX = 0;
      if (!direction) {
        return;
      }
      execute(direction > 0 ? this._config.rightCallback : this._config.leftCallback);
    }
    _initEvents() {
      if (this._supportPointerEvents) {
        EventHandler.on(this._element, EVENT_POINTERDOWN, event => this._start(event));
        EventHandler.on(this._element, EVENT_POINTERUP, event => this._end(event));
        this._element.classList.add(CLASS_NAME_POINTER_EVENT);
      } else {
        EventHandler.on(this._element, EVENT_TOUCHSTART, event => this._start(event));
        EventHandler.on(this._element, EVENT_TOUCHMOVE, event => this._move(event));
        EventHandler.on(this._element, EVENT_TOUCHEND, event => this._end(event));
      }
    }
    _eventIsPointerPenTouch(event) {
      return this._supportPointerEvents && (event.pointerType === POINTER_TYPE_PEN || event.pointerType === POINTER_TYPE_TOUCH);
    }

    // Static
    static isSupported() {
      return 'ontouchstart' in document.documentElement || navigator.maxTouchPoints > 0;
    }
  }

  /**
   * --------------------------------------------------------------------------
   * Bootstrap carousel.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$c = 'carousel';
  const DATA_KEY$8 = 'bs.carousel';
  const EVENT_KEY$8 = `.${DATA_KEY$8}`;
  const DATA_API_KEY$5 = '.data-api';
  const ARROW_LEFT_KEY$1 = 'ArrowLeft';
  const ARROW_RIGHT_KEY$1 = 'ArrowRight';
  const TOUCHEVENT_COMPAT_WAIT = 500; // Time for mouse compat events to fire after touch

  const ORDER_NEXT = 'next';
  const ORDER_PREV = 'prev';
  const DIRECTION_LEFT = 'left';
  const DIRECTION_RIGHT = 'right';
  const EVENT_SLIDE = `slide${EVENT_KEY$8}`;
  const EVENT_SLID = `slid${EVENT_KEY$8}`;
  const EVENT_KEYDOWN$1 = `keydown${EVENT_KEY$8}`;
  const EVENT_MOUSEENTER$1 = `mouseenter${EVENT_KEY$8}`;
  const EVENT_MOUSELEAVE$1 = `mouseleave${EVENT_KEY$8}`;
  const EVENT_DRAG_START = `dragstart${EVENT_KEY$8}`;
  const EVENT_LOAD_DATA_API$3 = `load${EVENT_KEY$8}${DATA_API_KEY$5}`;
  const EVENT_CLICK_DATA_API$5 = `click${EVENT_KEY$8}${DATA_API_KEY$5}`;
  const CLASS_NAME_CAROUSEL = 'carousel';
  const CLASS_NAME_ACTIVE$2 = 'active';
  const CLASS_NAME_SLIDE = 'slide';
  const CLASS_NAME_END = 'carousel-item-end';
  const CLASS_NAME_START = 'carousel-item-start';
  const CLASS_NAME_NEXT = 'carousel-item-next';
  const CLASS_NAME_PREV = 'carousel-item-prev';
  const SELECTOR_ACTIVE = '.active';
  const SELECTOR_ITEM = '.carousel-item';
  const SELECTOR_ACTIVE_ITEM = SELECTOR_ACTIVE + SELECTOR_ITEM;
  const SELECTOR_ITEM_IMG = '.carousel-item img';
  const SELECTOR_INDICATORS = '.carousel-indicators';
  const SELECTOR_DATA_SLIDE = '[data-bs-slide], [data-bs-slide-to]';
  const SELECTOR_DATA_RIDE = '[data-bs-ride="carousel"]';
  const KEY_TO_DIRECTION = {
    [ARROW_LEFT_KEY$1]: DIRECTION_RIGHT,
    [ARROW_RIGHT_KEY$1]: DIRECTION_LEFT
  };
  const Default$b = {
    interval: 5000,
    keyboard: true,
    pause: 'hover',
    ride: false,
    touch: true,
    wrap: true
  };
  const DefaultType$b = {
    interval: '(number|boolean)',
    // TODO:v6 remove boolean support
    keyboard: 'boolean',
    pause: '(string|boolean)',
    ride: '(boolean|string)',
    touch: 'boolean',
    wrap: 'boolean'
  };

  /**
   * Class definition
   */

  class Carousel extends BaseComponent {
    constructor(element, config) {
      super(element, config);
      this._interval = null;
      this._activeElement = null;
      this._isSliding = false;
      this.touchTimeout = null;
      this._swipeHelper = null;
      this._indicatorsElement = SelectorEngine.findOne(SELECTOR_INDICATORS, this._element);
      this._addEventListeners();
      if (this._config.ride === CLASS_NAME_CAROUSEL) {
        this.cycle();
      }
    }

    // Getters
    static get Default() {
      return Default$b;
    }
    static get DefaultType() {
      return DefaultType$b;
    }
    static get NAME() {
      return NAME$c;
    }

    // Public
    next() {
      this._slide(ORDER_NEXT);
    }
    nextWhenVisible() {
      // FIXME TODO use `document.visibilityState`
      // Don't call next when the page isn't visible
      // or the carousel or its parent isn't visible
      if (!document.hidden && isVisible(this._element)) {
        this.next();
      }
    }
    prev() {
      this._slide(ORDER_PREV);
    }
    pause() {
      if (this._isSliding) {
        triggerTransitionEnd(this._element);
      }
      this._clearInterval();
    }
    cycle() {
      this._clearInterval();
      this._updateInterval();
      this._interval = setInterval(() => this.nextWhenVisible(), this._config.interval);
    }
    _maybeEnableCycle() {
      if (!this._config.ride) {
        return;
      }
      if (this._isSliding) {
        EventHandler.one(this._element, EVENT_SLID, () => this.cycle());
        return;
      }
      this.cycle();
    }
    to(index) {
      const items = this._getItems();
      if (index > items.length - 1 || index < 0) {
        return;
      }
      if (this._isSliding) {
        EventHandler.one(this._element, EVENT_SLID, () => this.to(index));
        return;
      }
      const activeIndex = this._getItemIndex(this._getActive());
      if (activeIndex === index) {
        return;
      }
      const order = index > activeIndex ? ORDER_NEXT : ORDER_PREV;
      this._slide(order, items[index]);
    }
    dispose() {
      if (this._swipeHelper) {
        this._swipeHelper.dispose();
      }
      super.dispose();
    }

    // Private
    _configAfterMerge(config) {
      config.defaultInterval = config.interval;
      return config;
    }
    _addEventListeners() {
      if (this._config.keyboard) {
        EventHandler.on(this._element, EVENT_KEYDOWN$1, event => this._keydown(event));
      }
      if (this._config.pause === 'hover') {
        EventHandler.on(this._element, EVENT_MOUSEENTER$1, () => this.pause());
        EventHandler.on(this._element, EVENT_MOUSELEAVE$1, () => this._maybeEnableCycle());
      }
      if (this._config.touch && Swipe.isSupported()) {
        this._addTouchEventListeners();
      }
    }
    _addTouchEventListeners() {
      for (const img of SelectorEngine.find(SELECTOR_ITEM_IMG, this._element)) {
        EventHandler.on(img, EVENT_DRAG_START, event => event.preventDefault());
      }
      const endCallBack = () => {
        if (this._config.pause !== 'hover') {
          return;
        }

        // If it's a touch-enabled device, mouseenter/leave are fired as
        // part of the mouse compatibility events on first tap - the carousel
        // would stop cycling until user tapped out of it;
        // here, we listen for touchend, explicitly pause the carousel
        // (as if it's the second time we tap on it, mouseenter compat event
        // is NOT fired) and after a timeout (to allow for mouse compatibility
        // events to fire) we explicitly restart cycling

        this.pause();
        if (this.touchTimeout) {
          clearTimeout(this.touchTimeout);
        }
        this.touchTimeout = setTimeout(() => this._maybeEnableCycle(), TOUCHEVENT_COMPAT_WAIT + this._config.interval);
      };
      const swipeConfig = {
        leftCallback: () => this._slide(this._directionToOrder(DIRECTION_LEFT)),
        rightCallback: () => this._slide(this._directionToOrder(DIRECTION_RIGHT)),
        endCallback: endCallBack
      };
      this._swipeHelper = new Swipe(this._element, swipeConfig);
    }
    _keydown(event) {
      if (/input|textarea/i.test(event.target.tagName)) {
        return;
      }
      const direction = KEY_TO_DIRECTION[event.key];
      if (direction) {
        event.preventDefault();
        this._slide(this._directionToOrder(direction));
      }
    }
    _getItemIndex(element) {
      return this._getItems().indexOf(element);
    }
    _setActiveIndicatorElement(index) {
      if (!this._indicatorsElement) {
        return;
      }
      const activeIndicator = SelectorEngine.findOne(SELECTOR_ACTIVE, this._indicatorsElement);
      activeIndicator.classList.remove(CLASS_NAME_ACTIVE$2);
      activeIndicator.removeAttribute('aria-current');
      const newActiveIndicator = SelectorEngine.findOne(`[data-bs-slide-to="${index}"]`, this._indicatorsElement);
      if (newActiveIndicator) {
        newActiveIndicator.classList.add(CLASS_NAME_ACTIVE$2);
        newActiveIndicator.setAttribute('aria-current', 'true');
      }
    }
    _updateInterval() {
      const element = this._activeElement || this._getActive();
      if (!element) {
        return;
      }
      const elementInterval = Number.parseInt(element.getAttribute('data-bs-interval'), 10);
      this._config.interval = elementInterval || this._config.defaultInterval;
    }
    _slide(order, element = null) {
      if (this._isSliding) {
        return;
      }
      const activeElement = this._getActive();
      const isNext = order === ORDER_NEXT;
      const nextElement = element || getNextActiveElement(this._getItems(), activeElement, isNext, this._config.wrap);
      if (nextElement === activeElement) {
        return;
      }
      const nextElementIndex = this._getItemIndex(nextElement);
      const triggerEvent = eventName => {
        return EventHandler.trigger(this._element, eventName, {
          relatedTarget: nextElement,
          direction: this._orderToDirection(order),
          from: this._getItemIndex(activeElement),
          to: nextElementIndex
        });
      };
      const slideEvent = triggerEvent(EVENT_SLIDE);
      if (slideEvent.defaultPrevented) {
        return;
      }
      if (!activeElement || !nextElement) {
        // Some weirdness is happening, so we bail
        // TODO: change tests that use empty divs to avoid this check
        return;
      }
      const isCycling = Boolean(this._interval);
      this.pause();
      this._isSliding = true;
      this._setActiveIndicatorElement(nextElementIndex);
      this._activeElement = nextElement;
      const directionalClassName = isNext ? CLASS_NAME_START : CLASS_NAME_END;
      const orderClassName = isNext ? CLASS_NAME_NEXT : CLASS_NAME_PREV;
      nextElement.classList.add(orderClassName);
      reflow(nextElement);
      activeElement.classList.add(directionalClassName);
      nextElement.classList.add(directionalClassName);
      const completeCallBack = () => {
        nextElement.classList.remove(directionalClassName, orderClassName);
        nextElement.classList.add(CLASS_NAME_ACTIVE$2);
        activeElement.classList.remove(CLASS_NAME_ACTIVE$2, orderClassName, directionalClassName);
        this._isSliding = false;
        triggerEvent(EVENT_SLID);
      };
      this._queueCallback(completeCallBack, activeElement, this._isAnimated());
      if (isCycling) {
        this.cycle();
      }
    }
    _isAnimated() {
      return this._element.classList.contains(CLASS_NAME_SLIDE);
    }
    _getActive() {
      return SelectorEngine.findOne(SELECTOR_ACTIVE_ITEM, this._element);
    }
    _getItems() {
      return SelectorEngine.find(SELECTOR_ITEM, this._element);
    }
    _clearInterval() {
      if (this._interval) {
        clearInterval(this._interval);
        this._interval = null;
      }
    }
    _directionToOrder(direction) {
      if (isRTL()) {
        return direction === DIRECTION_LEFT ? ORDER_PREV : ORDER_NEXT;
      }
      return direction === DIRECTION_LEFT ? ORDER_NEXT : ORDER_PREV;
    }
    _orderToDirection(order) {
      if (isRTL()) {
        return order === ORDER_PREV ? DIRECTION_LEFT : DIRECTION_RIGHT;
      }
      return order === ORDER_PREV ? DIRECTION_RIGHT : DIRECTION_LEFT;
    }

    // Static
    static jQueryInterface(config) {
      return this.each(function () {
        const data = Carousel.getOrCreateInstance(this, config);
        if (typeof config === 'number') {
          data.to(config);
          return;
        }
        if (typeof config === 'string') {
          if (data[config] === undefined || config.startsWith('_') || config === 'constructor') {
            throw new TypeError(`No method named "${config}"`);
          }
          data[config]();
        }
      });
    }
  }

  /**
   * Data API implementation
   */

  EventHandler.on(document, EVENT_CLICK_DATA_API$5, SELECTOR_DATA_SLIDE, function (event) {
    const target = SelectorEngine.getElementFromSelector(this);
    if (!target || !target.classList.contains(CLASS_NAME_CAROUSEL)) {
      return;
    }
    event.preventDefault();
    const carousel = Carousel.getOrCreateInstance(target);
    const slideIndex = this.getAttribute('data-bs-slide-to');
    if (slideIndex) {
      carousel.to(slideIndex);
      carousel._maybeEnableCycle();
      return;
    }
    if (Manipulator.getDataAttribute(this, 'slide') === 'next') {
      carousel.next();
      carousel._maybeEnableCycle();
      return;
    }
    carousel.prev();
    carousel._maybeEnableCycle();
  });
  EventHandler.on(window, EVENT_LOAD_DATA_API$3, () => {
    const carousels = SelectorEngine.find(SELECTOR_DATA_RIDE);
    for (const carousel of carousels) {
      Carousel.getOrCreateInstance(carousel);
    }
  });

  /**
   * jQuery
   */

  defineJQueryPlugin(Carousel);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap collapse.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$b = 'collapse';
  const DATA_KEY$7 = 'bs.collapse';
  const EVENT_KEY$7 = `.${DATA_KEY$7}`;
  const DATA_API_KEY$4 = '.data-api';
  const EVENT_SHOW$6 = `show${EVENT_KEY$7}`;
  const EVENT_SHOWN$6 = `shown${EVENT_KEY$7}`;
  const EVENT_HIDE$6 = `hide${EVENT_KEY$7}`;
  const EVENT_HIDDEN$6 = `hidden${EVENT_KEY$7}`;
  const EVENT_CLICK_DATA_API$4 = `click${EVENT_KEY$7}${DATA_API_KEY$4}`;
  const CLASS_NAME_SHOW$7 = 'show';
  const CLASS_NAME_COLLAPSE = 'collapse';
  const CLASS_NAME_COLLAPSING = 'collapsing';
  const CLASS_NAME_COLLAPSED = 'collapsed';
  const CLASS_NAME_DEEPER_CHILDREN = `:scope .${CLASS_NAME_COLLAPSE} .${CLASS_NAME_COLLAPSE}`;
  const CLASS_NAME_HORIZONTAL = 'collapse-horizontal';
  const WIDTH = 'width';
  const HEIGHT = 'height';
  const SELECTOR_ACTIVES = '.collapse.show, .collapse.collapsing';
  const SELECTOR_DATA_TOGGLE$4 = '[data-bs-toggle="collapse"]';
  const Default$a = {
    parent: null,
    toggle: true
  };
  const DefaultType$a = {
    parent: '(null|element)',
    toggle: 'boolean'
  };

  /**
   * Class definition
   */

  class Collapse extends BaseComponent {
    constructor(element, config) {
      super(element, config);
      this._isTransitioning = false;
      this._triggerArray = [];
      const toggleList = SelectorEngine.find(SELECTOR_DATA_TOGGLE$4);
      for (const elem of toggleList) {
        const selector = SelectorEngine.getSelectorFromElement(elem);
        const filterElement = SelectorEngine.find(selector).filter(foundElement => foundElement === this._element);
        if (selector !== null && filterElement.length) {
          this._triggerArray.push(elem);
        }
      }
      this._initializeChildren();
      if (!this._config.parent) {
        this._addAriaAndCollapsedClass(this._triggerArray, this._isShown());
      }
      if (this._config.toggle) {
        this.toggle();
      }
    }

    // Getters
    static get Default() {
      return Default$a;
    }
    static get DefaultType() {
      return DefaultType$a;
    }
    static get NAME() {
      return NAME$b;
    }

    // Public
    toggle() {
      if (this._isShown()) {
        this.hide();
      } else {
        this.show();
      }
    }
    show() {
      if (this._isTransitioning || this._isShown()) {
        return;
      }
      let activeChildren = [];

      // find active children
      if (this._config.parent) {
        activeChildren = this._getFirstLevelChildren(SELECTOR_ACTIVES).filter(element => element !== this._element).map(element => Collapse.getOrCreateInstance(element, {
          toggle: false
        }));
      }
      if (activeChildren.length && activeChildren[0]._isTransitioning) {
        return;
      }
      const startEvent = EventHandler.trigger(this._element, EVENT_SHOW$6);
      if (startEvent.defaultPrevented) {
        return;
      }
      for (const activeInstance of activeChildren) {
        activeInstance.hide();
      }
      const dimension = this._getDimension();
      this._element.classList.remove(CLASS_NAME_COLLAPSE);
      this._element.classList.add(CLASS_NAME_COLLAPSING);
      this._element.style[dimension] = 0;
      this._addAriaAndCollapsedClass(this._triggerArray, true);
      this._isTransitioning = true;
      const complete = () => {
        this._isTransitioning = false;
        this._element.classList.remove(CLASS_NAME_COLLAPSING);
        this._element.classList.add(CLASS_NAME_COLLAPSE, CLASS_NAME_SHOW$7);
        this._element.style[dimension] = '';
        EventHandler.trigger(this._element, EVENT_SHOWN$6);
      };
      const capitalizedDimension = dimension[0].toUpperCase() + dimension.slice(1);
      const scrollSize = `scroll${capitalizedDimension}`;
      this._queueCallback(complete, this._element, true);
      this._element.style[dimension] = `${this._element[scrollSize]}px`;
    }
    hide() {
      if (this._isTransitioning || !this._isShown()) {
        return;
      }
      const startEvent = EventHandler.trigger(this._element, EVENT_HIDE$6);
      if (startEvent.defaultPrevented) {
        return;
      }
      const dimension = this._getDimension();
      this._element.style[dimension] = `${this._element.getBoundingClientRect()[dimension]}px`;
      reflow(this._element);
      this._element.classList.add(CLASS_NAME_COLLAPSING);
      this._element.classList.remove(CLASS_NAME_COLLAPSE, CLASS_NAME_SHOW$7);
      for (const trigger of this._triggerArray) {
        const element = SelectorEngine.getElementFromSelector(trigger);
        if (element && !this._isShown(element)) {
          this._addAriaAndCollapsedClass([trigger], false);
        }
      }
      this._isTransitioning = true;
      const complete = () => {
        this._isTransitioning = false;
        this._element.classList.remove(CLASS_NAME_COLLAPSING);
        this._element.classList.add(CLASS_NAME_COLLAPSE);
        EventHandler.trigger(this._element, EVENT_HIDDEN$6);
      };
      this._element.style[dimension] = '';
      this._queueCallback(complete, this._element, true);
    }
    _isShown(element = this._element) {
      return element.classList.contains(CLASS_NAME_SHOW$7);
    }

    // Private
    _configAfterMerge(config) {
      config.toggle = Boolean(config.toggle); // Coerce string values
      config.parent = getElement(config.parent);
      return config;
    }
    _getDimension() {
      return this._element.classList.contains(CLASS_NAME_HORIZONTAL) ? WIDTH : HEIGHT;
    }
    _initializeChildren() {
      if (!this._config.parent) {
        return;
      }
      const children = this._getFirstLevelChildren(SELECTOR_DATA_TOGGLE$4);
      for (const element of children) {
        const selected = SelectorEngine.getElementFromSelector(element);
        if (selected) {
          this._addAriaAndCollapsedClass([element], this._isShown(selected));
        }
      }
    }
    _getFirstLevelChildren(selector) {
      const children = SelectorEngine.find(CLASS_NAME_DEEPER_CHILDREN, this._config.parent);
      // remove children if greater depth
      return SelectorEngine.find(selector, this._config.parent).filter(element => !children.includes(element));
    }
    _addAriaAndCollapsedClass(triggerArray, isOpen) {
      if (!triggerArray.length) {
        return;
      }
      for (const element of triggerArray) {
        element.classList.toggle(CLASS_NAME_COLLAPSED, !isOpen);
        element.setAttribute('aria-expanded', isOpen);
      }
    }

    // Static
    static jQueryInterface(config) {
      const _config = {};
      if (typeof config === 'string' && /show|hide/.test(config)) {
        _config.toggle = false;
      }
      return this.each(function () {
        const data = Collapse.getOrCreateInstance(this, _config);
        if (typeof config === 'string') {
          if (typeof data[config] === 'undefined') {
            throw new TypeError(`No method named "${config}"`);
          }
          data[config]();
        }
      });
    }
  }

  /**
   * Data API implementation
   */

  EventHandler.on(document, EVENT_CLICK_DATA_API$4, SELECTOR_DATA_TOGGLE$4, function (event) {
    // preventDefault only for <a> elements (which change the URL) not inside the collapsible element
    if (event.target.tagName === 'A' || event.delegateTarget && event.delegateTarget.tagName === 'A') {
      event.preventDefault();
    }
    for (const element of SelectorEngine.getMultipleElementsFromSelector(this)) {
      Collapse.getOrCreateInstance(element, {
        toggle: false
      }).toggle();
    }
  });

  /**
   * jQuery
   */

  defineJQueryPlugin(Collapse);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap dropdown.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$a = 'dropdown';
  const DATA_KEY$6 = 'bs.dropdown';
  const EVENT_KEY$6 = `.${DATA_KEY$6}`;
  const DATA_API_KEY$3 = '.data-api';
  const ESCAPE_KEY$2 = 'Escape';
  const TAB_KEY$1 = 'Tab';
  const ARROW_UP_KEY$1 = 'ArrowUp';
  const ARROW_DOWN_KEY$1 = 'ArrowDown';
  const RIGHT_MOUSE_BUTTON = 2; // MouseEvent.button value for the secondary button, usually the right button

  const EVENT_HIDE$5 = `hide${EVENT_KEY$6}`;
  const EVENT_HIDDEN$5 = `hidden${EVENT_KEY$6}`;
  const EVENT_SHOW$5 = `show${EVENT_KEY$6}`;
  const EVENT_SHOWN$5 = `shown${EVENT_KEY$6}`;
  const EVENT_CLICK_DATA_API$3 = `click${EVENT_KEY$6}${DATA_API_KEY$3}`;
  const EVENT_KEYDOWN_DATA_API = `keydown${EVENT_KEY$6}${DATA_API_KEY$3}`;
  const EVENT_KEYUP_DATA_API = `keyup${EVENT_KEY$6}${DATA_API_KEY$3}`;
  const CLASS_NAME_SHOW$6 = 'show';
  const CLASS_NAME_DROPUP = 'dropup';
  const CLASS_NAME_DROPEND = 'dropend';
  const CLASS_NAME_DROPSTART = 'dropstart';
  const CLASS_NAME_DROPUP_CENTER = 'dropup-center';
  const CLASS_NAME_DROPDOWN_CENTER = 'dropdown-center';
  const SELECTOR_DATA_TOGGLE$3 = '[data-bs-toggle="dropdown"]:not(.disabled):not(:disabled)';
  const SELECTOR_DATA_TOGGLE_SHOWN = `${SELECTOR_DATA_TOGGLE$3}.${CLASS_NAME_SHOW$6}`;
  const SELECTOR_MENU = '.dropdown-menu';
  const SELECTOR_NAVBAR = '.navbar';
  const SELECTOR_NAVBAR_NAV = '.navbar-nav';
  const SELECTOR_VISIBLE_ITEMS = '.dropdown-menu .dropdown-item:not(.disabled):not(:disabled)';
  const PLACEMENT_TOP = isRTL() ? 'top-end' : 'top-start';
  const PLACEMENT_TOPEND = isRTL() ? 'top-start' : 'top-end';
  const PLACEMENT_BOTTOM = isRTL() ? 'bottom-end' : 'bottom-start';
  const PLACEMENT_BOTTOMEND = isRTL() ? 'bottom-start' : 'bottom-end';
  const PLACEMENT_RIGHT = isRTL() ? 'left-start' : 'right-start';
  const PLACEMENT_LEFT = isRTL() ? 'right-start' : 'left-start';
  const PLACEMENT_TOPCENTER = 'top';
  const PLACEMENT_BOTTOMCENTER = 'bottom';
  const Default$9 = {
    autoClose: true,
    boundary: 'clippingParents',
    display: 'dynamic',
    offset: [0, 2],
    popperConfig: null,
    reference: 'toggle'
  };
  const DefaultType$9 = {
    autoClose: '(boolean|string)',
    boundary: '(string|element)',
    display: 'string',
    offset: '(array|string|function)',
    popperConfig: '(null|object|function)',
    reference: '(string|element|object)'
  };

  /**
   * Class definition
   */

  class Dropdown extends BaseComponent {
    constructor(element, config) {
      super(element, config);
      this._popper = null;
      this._parent = this._element.parentNode; // dropdown wrapper
      // TODO: v6 revert #37011 & change markup https://getbootstrap.com/docs/5.3/forms/input-group/
      this._menu = SelectorEngine.next(this._element, SELECTOR_MENU)[0] || SelectorEngine.prev(this._element, SELECTOR_MENU)[0] || SelectorEngine.findOne(SELECTOR_MENU, this._parent);
      this._inNavbar = this._detectNavbar();
    }

    // Getters
    static get Default() {
      return Default$9;
    }
    static get DefaultType() {
      return DefaultType$9;
    }
    static get NAME() {
      return NAME$a;
    }

    // Public
    toggle() {
      return this._isShown() ? this.hide() : this.show();
    }
    show() {
      if (isDisabled(this._element) || this._isShown()) {
        return;
      }
      const relatedTarget = {
        relatedTarget: this._element
      };
      const showEvent = EventHandler.trigger(this._element, EVENT_SHOW$5, relatedTarget);
      if (showEvent.defaultPrevented) {
        return;
      }
      this._createPopper();

      // If this is a touch-enabled device we add extra
      // empty mouseover listeners to the body's immediate children;
      // only needed because of broken event delegation on iOS
      // https://www.quirksmode.org/blog/archives/2014/02/mouse_event_bub.html
      if ('ontouchstart' in document.documentElement && !this._parent.closest(SELECTOR_NAVBAR_NAV)) {
        for (const element of [].concat(...document.body.children)) {
          EventHandler.on(element, 'mouseover', noop);
        }
      }
      this._element.focus();
      this._element.setAttribute('aria-expanded', true);
      this._menu.classList.add(CLASS_NAME_SHOW$6);
      this._element.classList.add(CLASS_NAME_SHOW$6);
      EventHandler.trigger(this._element, EVENT_SHOWN$5, relatedTarget);
    }
    hide() {
      if (isDisabled(this._element) || !this._isShown()) {
        return;
      }
      const relatedTarget = {
        relatedTarget: this._element
      };
      this._completeHide(relatedTarget);
    }
    dispose() {
      if (this._popper) {
        this._popper.destroy();
      }
      super.dispose();
    }
    update() {
      this._inNavbar = this._detectNavbar();
      if (this._popper) {
        this._popper.update();
      }
    }

    // Private
    _completeHide(relatedTarget) {
      const hideEvent = EventHandler.trigger(this._element, EVENT_HIDE$5, relatedTarget);
      if (hideEvent.defaultPrevented) {
        return;
      }

      // If this is a touch-enabled device we remove the extra
      // empty mouseover listeners we added for iOS support
      if ('ontouchstart' in document.documentElement) {
        for (const element of [].concat(...document.body.children)) {
          EventHandler.off(element, 'mouseover', noop);
        }
      }
      if (this._popper) {
        this._popper.destroy();
      }
      this._menu.classList.remove(CLASS_NAME_SHOW$6);
      this._element.classList.remove(CLASS_NAME_SHOW$6);
      this._element.setAttribute('aria-expanded', 'false');
      Manipulator.removeDataAttribute(this._menu, 'popper');
      EventHandler.trigger(this._element, EVENT_HIDDEN$5, relatedTarget);
    }
    _getConfig(config) {
      config = super._getConfig(config);
      if (typeof config.reference === 'object' && !isElement(config.reference) && typeof config.reference.getBoundingClientRect !== 'function') {
        // Popper virtual elements require a getBoundingClientRect method
        throw new TypeError(`${NAME$a.toUpperCase()}: Option "reference" provided type "object" without a required "getBoundingClientRect" method.`);
      }
      return config;
    }
    _createPopper() {
      if (typeof Popper__namespace === 'undefined') {
        throw new TypeError('Bootstrap\'s dropdowns require Popper (https://popper.js.org)');
      }
      let referenceElement = this._element;
      if (this._config.reference === 'parent') {
        referenceElement = this._parent;
      } else if (isElement(this._config.reference)) {
        referenceElement = getElement(this._config.reference);
      } else if (typeof this._config.reference === 'object') {
        referenceElement = this._config.reference;
      }
      const popperConfig = this._getPopperConfig();
      this._popper = Popper__namespace.createPopper(referenceElement, this._menu, popperConfig);
    }
    _isShown() {
      return this._menu.classList.contains(CLASS_NAME_SHOW$6);
    }
    _getPlacement() {
      const parentDropdown = this._parent;
      if (parentDropdown.classList.contains(CLASS_NAME_DROPEND)) {
        return PLACEMENT_RIGHT;
      }
      if (parentDropdown.classList.contains(CLASS_NAME_DROPSTART)) {
        return PLACEMENT_LEFT;
      }
      if (parentDropdown.classList.contains(CLASS_NAME_DROPUP_CENTER)) {
        return PLACEMENT_TOPCENTER;
      }
      if (parentDropdown.classList.contains(CLASS_NAME_DROPDOWN_CENTER)) {
        return PLACEMENT_BOTTOMCENTER;
      }

      // We need to trim the value because custom properties can also include spaces
      const isEnd = getComputedStyle(this._menu).getPropertyValue('--bs-position').trim() === 'end';
      if (parentDropdown.classList.contains(CLASS_NAME_DROPUP)) {
        return isEnd ? PLACEMENT_TOPEND : PLACEMENT_TOP;
      }
      return isEnd ? PLACEMENT_BOTTOMEND : PLACEMENT_BOTTOM;
    }
    _detectNavbar() {
      return this._element.closest(SELECTOR_NAVBAR) !== null;
    }
    _getOffset() {
      const {
        offset
      } = this._config;
      if (typeof offset === 'string') {
        return offset.split(',').map(value => Number.parseInt(value, 10));
      }
      if (typeof offset === 'function') {
        return popperData => offset(popperData, this._element);
      }
      return offset;
    }
    _getPopperConfig() {
      const defaultBsPopperConfig = {
        placement: this._getPlacement(),
        modifiers: [{
          name: 'preventOverflow',
          options: {
            boundary: this._config.boundary
          }
        }, {
          name: 'offset',
          options: {
            offset: this._getOffset()
          }
        }]
      };

      // Disable Popper if we have a static display or Dropdown is in Navbar
      if (this._inNavbar || this._config.display === 'static') {
        Manipulator.setDataAttribute(this._menu, 'popper', 'static'); // TODO: v6 remove
        defaultBsPopperConfig.modifiers = [{
          name: 'applyStyles',
          enabled: false
        }];
      }
      return {
        ...defaultBsPopperConfig,
        ...execute(this._config.popperConfig, [defaultBsPopperConfig])
      };
    }
    _selectMenuItem({
      key,
      target
    }) {
      const items = SelectorEngine.find(SELECTOR_VISIBLE_ITEMS, this._menu).filter(element => isVisible(element));
      if (!items.length) {
        return;
      }

      // if target isn't included in items (e.g. when expanding the dropdown)
      // allow cycling to get the last item in case key equals ARROW_UP_KEY
      getNextActiveElement(items, target, key === ARROW_DOWN_KEY$1, !items.includes(target)).focus();
    }

    // Static
    static jQueryInterface(config) {
      return this.each(function () {
        const data = Dropdown.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (typeof data[config] === 'undefined') {
          throw new TypeError(`No method named "${config}"`);
        }
        data[config]();
      });
    }
    static clearMenus(event) {
      if (event.button === RIGHT_MOUSE_BUTTON || event.type === 'keyup' && event.key !== TAB_KEY$1) {
        return;
      }
      const openToggles = SelectorEngine.find(SELECTOR_DATA_TOGGLE_SHOWN);
      for (const toggle of openToggles) {
        const context = Dropdown.getInstance(toggle);
        if (!context || context._config.autoClose === false) {
          continue;
        }
        const composedPath = event.composedPath();
        const isMenuTarget = composedPath.includes(context._menu);
        if (composedPath.includes(context._element) || context._config.autoClose === 'inside' && !isMenuTarget || context._config.autoClose === 'outside' && isMenuTarget) {
          continue;
        }

        // Tab navigation through the dropdown menu or events from contained inputs shouldn't close the menu
        if (context._menu.contains(event.target) && (event.type === 'keyup' && event.key === TAB_KEY$1 || /input|select|option|textarea|form/i.test(event.target.tagName))) {
          continue;
        }
        const relatedTarget = {
          relatedTarget: context._element
        };
        if (event.type === 'click') {
          relatedTarget.clickEvent = event;
        }
        context._completeHide(relatedTarget);
      }
    }
    static dataApiKeydownHandler(event) {
      // If not an UP | DOWN | ESCAPE key => not a dropdown command
      // If input/textarea && if key is other than ESCAPE => not a dropdown command

      const isInput = /input|textarea/i.test(event.target.tagName);
      const isEscapeEvent = event.key === ESCAPE_KEY$2;
      const isUpOrDownEvent = [ARROW_UP_KEY$1, ARROW_DOWN_KEY$1].includes(event.key);
      if (!isUpOrDownEvent && !isEscapeEvent) {
        return;
      }
      if (isInput && !isEscapeEvent) {
        return;
      }
      event.preventDefault();

      // TODO: v6 revert #37011 & change markup https://getbootstrap.com/docs/5.3/forms/input-group/
      const getToggleButton = this.matches(SELECTOR_DATA_TOGGLE$3) ? this : SelectorEngine.prev(this, SELECTOR_DATA_TOGGLE$3)[0] || SelectorEngine.next(this, SELECTOR_DATA_TOGGLE$3)[0] || SelectorEngine.findOne(SELECTOR_DATA_TOGGLE$3, event.delegateTarget.parentNode);
      const instance = Dropdown.getOrCreateInstance(getToggleButton);
      if (isUpOrDownEvent) {
        event.stopPropagation();
        instance.show();
        instance._selectMenuItem(event);
        return;
      }
      if (instance._isShown()) {
        // else is escape and we check if it is shown
        event.stopPropagation();
        instance.hide();
        getToggleButton.focus();
      }
    }
  }

  /**
   * Data API implementation
   */

  EventHandler.on(document, EVENT_KEYDOWN_DATA_API, SELECTOR_DATA_TOGGLE$3, Dropdown.dataApiKeydownHandler);
  EventHandler.on(document, EVENT_KEYDOWN_DATA_API, SELECTOR_MENU, Dropdown.dataApiKeydownHandler);
  EventHandler.on(document, EVENT_CLICK_DATA_API$3, Dropdown.clearMenus);
  EventHandler.on(document, EVENT_KEYUP_DATA_API, Dropdown.clearMenus);
  EventHandler.on(document, EVENT_CLICK_DATA_API$3, SELECTOR_DATA_TOGGLE$3, function (event) {
    event.preventDefault();
    Dropdown.getOrCreateInstance(this).toggle();
  });

  /**
   * jQuery
   */

  defineJQueryPlugin(Dropdown);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/backdrop.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$9 = 'backdrop';
  const CLASS_NAME_FADE$4 = 'fade';
  const CLASS_NAME_SHOW$5 = 'show';
  const EVENT_MOUSEDOWN = `mousedown.bs.${NAME$9}`;
  const Default$8 = {
    className: 'modal-backdrop',
    clickCallback: null,
    isAnimated: false,
    isVisible: true,
    // if false, we use the backdrop helper without adding any element to the dom
    rootElement: 'body' // give the choice to place backdrop under different elements
  };
  const DefaultType$8 = {
    className: 'string',
    clickCallback: '(function|null)',
    isAnimated: 'boolean',
    isVisible: 'boolean',
    rootElement: '(element|string)'
  };

  /**
   * Class definition
   */

  class Backdrop extends Config {
    constructor(config) {
      super();
      this._config = this._getConfig(config);
      this._isAppended = false;
      this._element = null;
    }

    // Getters
    static get Default() {
      return Default$8;
    }
    static get DefaultType() {
      return DefaultType$8;
    }
    static get NAME() {
      return NAME$9;
    }

    // Public
    show(callback) {
      if (!this._config.isVisible) {
        execute(callback);
        return;
      }
      this._append();
      const element = this._getElement();
      if (this._config.isAnimated) {
        reflow(element);
      }
      element.classList.add(CLASS_NAME_SHOW$5);
      this._emulateAnimation(() => {
        execute(callback);
      });
    }
    hide(callback) {
      if (!this._config.isVisible) {
        execute(callback);
        return;
      }
      this._getElement().classList.remove(CLASS_NAME_SHOW$5);
      this._emulateAnimation(() => {
        this.dispose();
        execute(callback);
      });
    }
    dispose() {
      if (!this._isAppended) {
        return;
      }
      EventHandler.off(this._element, EVENT_MOUSEDOWN);
      this._element.remove();
      this._isAppended = false;
    }

    // Private
    _getElement() {
      if (!this._element) {
        const backdrop = document.createElement('div');
        backdrop.className = this._config.className;
        if (this._config.isAnimated) {
          backdrop.classList.add(CLASS_NAME_FADE$4);
        }
        this._element = backdrop;
      }
      return this._element;
    }
    _configAfterMerge(config) {
      // use getElement() with the default "body" to get a fresh Element on each instantiation
      config.rootElement = getElement(config.rootElement);
      return config;
    }
    _append() {
      if (this._isAppended) {
        return;
      }
      const element = this._getElement();
      this._config.rootElement.append(element);
      EventHandler.on(element, EVENT_MOUSEDOWN, () => {
        execute(this._config.clickCallback);
      });
      this._isAppended = true;
    }
    _emulateAnimation(callback) {
      executeAfterTransition(callback, this._getElement(), this._config.isAnimated);
    }
  }

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/focustrap.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$8 = 'focustrap';
  const DATA_KEY$5 = 'bs.focustrap';
  const EVENT_KEY$5 = `.${DATA_KEY$5}`;
  const EVENT_FOCUSIN$2 = `focusin${EVENT_KEY$5}`;
  const EVENT_KEYDOWN_TAB = `keydown.tab${EVENT_KEY$5}`;
  const TAB_KEY = 'Tab';
  const TAB_NAV_FORWARD = 'forward';
  const TAB_NAV_BACKWARD = 'backward';
  const Default$7 = {
    autofocus: true,
    trapElement: null // The element to trap focus inside of
  };
  const DefaultType$7 = {
    autofocus: 'boolean',
    trapElement: 'element'
  };

  /**
   * Class definition
   */

  class FocusTrap extends Config {
    constructor(config) {
      super();
      this._config = this._getConfig(config);
      this._isActive = false;
      this._lastTabNavDirection = null;
    }

    // Getters
    static get Default() {
      return Default$7;
    }
    static get DefaultType() {
      return DefaultType$7;
    }
    static get NAME() {
      return NAME$8;
    }

    // Public
    activate() {
      if (this._isActive) {
        return;
      }
      if (this._config.autofocus) {
        this._config.trapElement.focus();
      }
      EventHandler.off(document, EVENT_KEY$5); // guard against infinite focus loop
      EventHandler.on(document, EVENT_FOCUSIN$2, event => this._handleFocusin(event));
      EventHandler.on(document, EVENT_KEYDOWN_TAB, event => this._handleKeydown(event));
      this._isActive = true;
    }
    deactivate() {
      if (!this._isActive) {
        return;
      }
      this._isActive = false;
      EventHandler.off(document, EVENT_KEY$5);
    }

    // Private
    _handleFocusin(event) {
      const {
        trapElement
      } = this._config;
      if (event.target === document || event.target === trapElement || trapElement.contains(event.target)) {
        return;
      }
      const elements = SelectorEngine.focusableChildren(trapElement);
      if (elements.length === 0) {
        trapElement.focus();
      } else if (this._lastTabNavDirection === TAB_NAV_BACKWARD) {
        elements[elements.length - 1].focus();
      } else {
        elements[0].focus();
      }
    }
    _handleKeydown(event) {
      if (event.key !== TAB_KEY) {
        return;
      }
      this._lastTabNavDirection = event.shiftKey ? TAB_NAV_BACKWARD : TAB_NAV_FORWARD;
    }
  }

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/scrollBar.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const SELECTOR_FIXED_CONTENT = '.fixed-top, .fixed-bottom, .is-fixed, .sticky-top';
  const SELECTOR_STICKY_CONTENT = '.sticky-top';
  const PROPERTY_PADDING = 'padding-right';
  const PROPERTY_MARGIN = 'margin-right';

  /**
   * Class definition
   */

  class ScrollBarHelper {
    constructor() {
      this._element = document.body;
    }

    // Public
    getWidth() {
      // https://developer.mozilla.org/en-US/docs/Web/API/Window/innerWidth#usage_notes
      const documentWidth = document.documentElement.clientWidth;
      return Math.abs(window.innerWidth - documentWidth);
    }
    hide() {
      const width = this.getWidth();
      this._disableOverFlow();
      // give padding to element to balance the hidden scrollbar width
      this._setElementAttributes(this._element, PROPERTY_PADDING, calculatedValue => calculatedValue + width);
      // trick: We adjust positive paddingRight and negative marginRight to sticky-top elements to keep showing fullwidth
      this._setElementAttributes(SELECTOR_FIXED_CONTENT, PROPERTY_PADDING, calculatedValue => calculatedValue + width);
      this._setElementAttributes(SELECTOR_STICKY_CONTENT, PROPERTY_MARGIN, calculatedValue => calculatedValue - width);
    }
    reset() {
      this._resetElementAttributes(this._element, 'overflow');
      this._resetElementAttributes(this._element, PROPERTY_PADDING);
      this._resetElementAttributes(SELECTOR_FIXED_CONTENT, PROPERTY_PADDING);
      this._resetElementAttributes(SELECTOR_STICKY_CONTENT, PROPERTY_MARGIN);
    }
    isOverflowing() {
      return this.getWidth() > 0;
    }

    // Private
    _disableOverFlow() {
      this._saveInitialAttribute(this._element, 'overflow');
      this._element.style.overflow = 'hidden';
    }
    _setElementAttributes(selector, styleProperty, callback) {
      const scrollbarWidth = this.getWidth();
      const manipulationCallBack = element => {
        if (element !== this._element && window.innerWidth > element.clientWidth + scrollbarWidth) {
          return;
        }
        this._saveInitialAttribute(element, styleProperty);
        const calculatedValue = window.getComputedStyle(element).getPropertyValue(styleProperty);
        element.style.setProperty(styleProperty, `${callback(Number.parseFloat(calculatedValue))}px`);
      };
      this._applyManipulationCallback(selector, manipulationCallBack);
    }
    _saveInitialAttribute(element, styleProperty) {
      const actualValue = element.style.getPropertyValue(styleProperty);
      if (actualValue) {
        Manipulator.setDataAttribute(element, styleProperty, actualValue);
      }
    }
    _resetElementAttributes(selector, styleProperty) {
      const manipulationCallBack = element => {
        const value = Manipulator.getDataAttribute(element, styleProperty);
        // We only want to remove the property if the value is `null`; the value can also be zero
        if (value === null) {
          element.style.removeProperty(styleProperty);
          return;
        }
        Manipulator.removeDataAttribute(element, styleProperty);
        element.style.setProperty(styleProperty, value);
      };
      this._applyManipulationCallback(selector, manipulationCallBack);
    }
    _applyManipulationCallback(selector, callBack) {
      if (isElement(selector)) {
        callBack(selector);
        return;
      }
      for (const sel of SelectorEngine.find(selector, this._element)) {
        callBack(sel);
      }
    }
  }

  /**
   * --------------------------------------------------------------------------
   * Bootstrap modal.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$7 = 'modal';
  const DATA_KEY$4 = 'bs.modal';
  const EVENT_KEY$4 = `.${DATA_KEY$4}`;
  const DATA_API_KEY$2 = '.data-api';
  const ESCAPE_KEY$1 = 'Escape';
  const EVENT_HIDE$4 = `hide${EVENT_KEY$4}`;
  const EVENT_HIDE_PREVENTED$1 = `hidePrevented${EVENT_KEY$4}`;
  const EVENT_HIDDEN$4 = `hidden${EVENT_KEY$4}`;
  const EVENT_SHOW$4 = `show${EVENT_KEY$4}`;
  const EVENT_SHOWN$4 = `shown${EVENT_KEY$4}`;
  const EVENT_RESIZE$1 = `resize${EVENT_KEY$4}`;
  const EVENT_CLICK_DISMISS = `click.dismiss${EVENT_KEY$4}`;
  const EVENT_MOUSEDOWN_DISMISS = `mousedown.dismiss${EVENT_KEY$4}`;
  const EVENT_KEYDOWN_DISMISS$1 = `keydown.dismiss${EVENT_KEY$4}`;
  const EVENT_CLICK_DATA_API$2 = `click${EVENT_KEY$4}${DATA_API_KEY$2}`;
  const CLASS_NAME_OPEN = 'modal-open';
  const CLASS_NAME_FADE$3 = 'fade';
  const CLASS_NAME_SHOW$4 = 'show';
  const CLASS_NAME_STATIC = 'modal-static';
  const OPEN_SELECTOR$1 = '.modal.show';
  const SELECTOR_DIALOG = '.modal-dialog';
  const SELECTOR_MODAL_BODY = '.modal-body';
  const SELECTOR_DATA_TOGGLE$2 = '[data-bs-toggle="modal"]';
  const Default$6 = {
    backdrop: true,
    focus: true,
    keyboard: true
  };
  const DefaultType$6 = {
    backdrop: '(boolean|string)',
    focus: 'boolean',
    keyboard: 'boolean'
  };

  /**
   * Class definition
   */

  class Modal extends BaseComponent {
    constructor(element, config) {
      super(element, config);
      this._dialog = SelectorEngine.findOne(SELECTOR_DIALOG, this._element);
      this._backdrop = this._initializeBackDrop();
      this._focustrap = this._initializeFocusTrap();
      this._isShown = false;
      this._isTransitioning = false;
      this._scrollBar = new ScrollBarHelper();
      this._addEventListeners();
    }

    // Getters
    static get Default() {
      return Default$6;
    }
    static get DefaultType() {
      return DefaultType$6;
    }
    static get NAME() {
      return NAME$7;
    }

    // Public
    toggle(relatedTarget) {
      return this._isShown ? this.hide() : this.show(relatedTarget);
    }
    show(relatedTarget) {
      if (this._isShown || this._isTransitioning) {
        return;
      }
      const showEvent = EventHandler.trigger(this._element, EVENT_SHOW$4, {
        relatedTarget
      });
      if (showEvent.defaultPrevented) {
        return;
      }
      this._isShown = true;
      this._isTransitioning = true;
      this._scrollBar.hide();
      document.body.classList.add(CLASS_NAME_OPEN);
      this._adjustDialog();
      this._backdrop.show(() => this._showElement(relatedTarget));
    }
    hide() {
      if (!this._isShown || this._isTransitioning) {
        return;
      }
      const hideEvent = EventHandler.trigger(this._element, EVENT_HIDE$4);
      if (hideEvent.defaultPrevented) {
        return;
      }
      this._isShown = false;
      this._isTransitioning = true;
      this._focustrap.deactivate();
      this._element.classList.remove(CLASS_NAME_SHOW$4);
      this._queueCallback(() => this._hideModal(), this._element, this._isAnimated());
    }
    dispose() {
      EventHandler.off(window, EVENT_KEY$4);
      EventHandler.off(this._dialog, EVENT_KEY$4);
      this._backdrop.dispose();
      this._focustrap.deactivate();
      super.dispose();
    }
    handleUpdate() {
      this._adjustDialog();
    }

    // Private
    _initializeBackDrop() {
      return new Backdrop({
        isVisible: Boolean(this._config.backdrop),
        // 'static' option will be translated to true, and booleans will keep their value,
        isAnimated: this._isAnimated()
      });
    }
    _initializeFocusTrap() {
      return new FocusTrap({
        trapElement: this._element
      });
    }
    _showElement(relatedTarget) {
      // try to append dynamic modal
      if (!document.body.contains(this._element)) {
        document.body.append(this._element);
      }
      this._element.style.display = 'block';
      this._element.removeAttribute('aria-hidden');
      this._element.setAttribute('aria-modal', true);
      this._element.setAttribute('role', 'dialog');
      this._element.scrollTop = 0;
      const modalBody = SelectorEngine.findOne(SELECTOR_MODAL_BODY, this._dialog);
      if (modalBody) {
        modalBody.scrollTop = 0;
      }
      reflow(this._element);
      this._element.classList.add(CLASS_NAME_SHOW$4);
      const transitionComplete = () => {
        if (this._config.focus) {
          this._focustrap.activate();
        }
        this._isTransitioning = false;
        EventHandler.trigger(this._element, EVENT_SHOWN$4, {
          relatedTarget
        });
      };
      this._queueCallback(transitionComplete, this._dialog, this._isAnimated());
    }
    _addEventListeners() {
      EventHandler.on(this._element, EVENT_KEYDOWN_DISMISS$1, event => {
        if (event.key !== ESCAPE_KEY$1) {
          return;
        }
        if (this._config.keyboard) {
          this.hide();
          return;
        }
        this._triggerBackdropTransition();
      });
      EventHandler.on(window, EVENT_RESIZE$1, () => {
        if (this._isShown && !this._isTransitioning) {
          this._adjustDialog();
        }
      });
      EventHandler.on(this._element, EVENT_MOUSEDOWN_DISMISS, event => {
        // a bad trick to segregate clicks that may start inside dialog but end outside, and avoid listen to scrollbar clicks
        EventHandler.one(this._element, EVENT_CLICK_DISMISS, event2 => {
          if (this._element !== event.target || this._element !== event2.target) {
            return;
          }
          if (this._config.backdrop === 'static') {
            this._triggerBackdropTransition();
            return;
          }
          if (this._config.backdrop) {
            this.hide();
          }
        });
      });
    }
    _hideModal() {
      this._element.style.display = 'none';
      this._element.setAttribute('aria-hidden', true);
      this._element.removeAttribute('aria-modal');
      this._element.removeAttribute('role');
      this._isTransitioning = false;
      this._backdrop.hide(() => {
        document.body.classList.remove(CLASS_NAME_OPEN);
        this._resetAdjustments();
        this._scrollBar.reset();
        EventHandler.trigger(this._element, EVENT_HIDDEN$4);
      });
    }
    _isAnimated() {
      return this._element.classList.contains(CLASS_NAME_FADE$3);
    }
    _triggerBackdropTransition() {
      const hideEvent = EventHandler.trigger(this._element, EVENT_HIDE_PREVENTED$1);
      if (hideEvent.defaultPrevented) {
        return;
      }
      const isModalOverflowing = this._element.scrollHeight > document.documentElement.clientHeight;
      const initialOverflowY = this._element.style.overflowY;
      // return if the following background transition hasn't yet completed
      if (initialOverflowY === 'hidden' || this._element.classList.contains(CLASS_NAME_STATIC)) {
        return;
      }
      if (!isModalOverflowing) {
        this._element.style.overflowY = 'hidden';
      }
      this._element.classList.add(CLASS_NAME_STATIC);
      this._queueCallback(() => {
        this._element.classList.remove(CLASS_NAME_STATIC);
        this._queueCallback(() => {
          this._element.style.overflowY = initialOverflowY;
        }, this._dialog);
      }, this._dialog);
      this._element.focus();
    }

    /**
     * The following methods are used to handle overflowing modals
     */

    _adjustDialog() {
      const isModalOverflowing = this._element.scrollHeight > document.documentElement.clientHeight;
      const scrollbarWidth = this._scrollBar.getWidth();
      const isBodyOverflowing = scrollbarWidth > 0;
      if (isBodyOverflowing && !isModalOverflowing) {
        const property = isRTL() ? 'paddingLeft' : 'paddingRight';
        this._element.style[property] = `${scrollbarWidth}px`;
      }
      if (!isBodyOverflowing && isModalOverflowing) {
        const property = isRTL() ? 'paddingRight' : 'paddingLeft';
        this._element.style[property] = `${scrollbarWidth}px`;
      }
    }
    _resetAdjustments() {
      this._element.style.paddingLeft = '';
      this._element.style.paddingRight = '';
    }

    // Static
    static jQueryInterface(config, relatedTarget) {
      return this.each(function () {
        const data = Modal.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (typeof data[config] === 'undefined') {
          throw new TypeError(`No method named "${config}"`);
        }
        data[config](relatedTarget);
      });
    }
  }

  /**
   * Data API implementation
   */

  EventHandler.on(document, EVENT_CLICK_DATA_API$2, SELECTOR_DATA_TOGGLE$2, function (event) {
    const target = SelectorEngine.getElementFromSelector(this);
    if (['A', 'AREA'].includes(this.tagName)) {
      event.preventDefault();
    }
    EventHandler.one(target, EVENT_SHOW$4, showEvent => {
      if (showEvent.defaultPrevented) {
        // only register focus restorer if modal will actually get shown
        return;
      }
      EventHandler.one(target, EVENT_HIDDEN$4, () => {
        if (isVisible(this)) {
          this.focus();
        }
      });
    });

    // avoid conflict when clicking modal toggler while another one is open
    const alreadyOpen = SelectorEngine.findOne(OPEN_SELECTOR$1);
    if (alreadyOpen) {
      Modal.getInstance(alreadyOpen).hide();
    }
    const data = Modal.getOrCreateInstance(target);
    data.toggle(this);
  });
  enableDismissTrigger(Modal);

  /**
   * jQuery
   */

  defineJQueryPlugin(Modal);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap offcanvas.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$6 = 'offcanvas';
  const DATA_KEY$3 = 'bs.offcanvas';
  const EVENT_KEY$3 = `.${DATA_KEY$3}`;
  const DATA_API_KEY$1 = '.data-api';
  const EVENT_LOAD_DATA_API$2 = `load${EVENT_KEY$3}${DATA_API_KEY$1}`;
  const ESCAPE_KEY = 'Escape';
  const CLASS_NAME_SHOW$3 = 'show';
  const CLASS_NAME_SHOWING$1 = 'showing';
  const CLASS_NAME_HIDING = 'hiding';
  const CLASS_NAME_BACKDROP = 'offcanvas-backdrop';
  const OPEN_SELECTOR = '.offcanvas.show';
  const EVENT_SHOW$3 = `show${EVENT_KEY$3}`;
  const EVENT_SHOWN$3 = `shown${EVENT_KEY$3}`;
  const EVENT_HIDE$3 = `hide${EVENT_KEY$3}`;
  const EVENT_HIDE_PREVENTED = `hidePrevented${EVENT_KEY$3}`;
  const EVENT_HIDDEN$3 = `hidden${EVENT_KEY$3}`;
  const EVENT_RESIZE = `resize${EVENT_KEY$3}`;
  const EVENT_CLICK_DATA_API$1 = `click${EVENT_KEY$3}${DATA_API_KEY$1}`;
  const EVENT_KEYDOWN_DISMISS = `keydown.dismiss${EVENT_KEY$3}`;
  const SELECTOR_DATA_TOGGLE$1 = '[data-bs-toggle="offcanvas"]';
  const Default$5 = {
    backdrop: true,
    keyboard: true,
    scroll: false
  };
  const DefaultType$5 = {
    backdrop: '(boolean|string)',
    keyboard: 'boolean',
    scroll: 'boolean'
  };

  /**
   * Class definition
   */

  class Offcanvas extends BaseComponent {
    constructor(element, config) {
      super(element, config);
      this._isShown = false;
      this._backdrop = this._initializeBackDrop();
      this._focustrap = this._initializeFocusTrap();
      this._addEventListeners();
    }

    // Getters
    static get Default() {
      return Default$5;
    }
    static get DefaultType() {
      return DefaultType$5;
    }
    static get NAME() {
      return NAME$6;
    }

    // Public
    toggle(relatedTarget) {
      return this._isShown ? this.hide() : this.show(relatedTarget);
    }
    show(relatedTarget) {
      if (this._isShown) {
        return;
      }
      const showEvent = EventHandler.trigger(this._element, EVENT_SHOW$3, {
        relatedTarget
      });
      if (showEvent.defaultPrevented) {
        return;
      }
      this._isShown = true;
      this._backdrop.show();
      if (!this._config.scroll) {
        new ScrollBarHelper().hide();
      }
      this._element.setAttribute('aria-modal', true);
      this._element.setAttribute('role', 'dialog');
      this._element.classList.add(CLASS_NAME_SHOWING$1);
      const completeCallBack = () => {
        if (!this._config.scroll || this._config.backdrop) {
          this._focustrap.activate();
        }
        this._element.classList.add(CLASS_NAME_SHOW$3);
        this._element.classList.remove(CLASS_NAME_SHOWING$1);
        EventHandler.trigger(this._element, EVENT_SHOWN$3, {
          relatedTarget
        });
      };
      this._queueCallback(completeCallBack, this._element, true);
    }
    hide() {
      if (!this._isShown) {
        return;
      }
      const hideEvent = EventHandler.trigger(this._element, EVENT_HIDE$3);
      if (hideEvent.defaultPrevented) {
        return;
      }
      this._focustrap.deactivate();
      this._element.blur();
      this._isShown = false;
      this._element.classList.add(CLASS_NAME_HIDING);
      this._backdrop.hide();
      const completeCallback = () => {
        this._element.classList.remove(CLASS_NAME_SHOW$3, CLASS_NAME_HIDING);
        this._element.removeAttribute('aria-modal');
        this._element.removeAttribute('role');
        if (!this._config.scroll) {
          new ScrollBarHelper().reset();
        }
        EventHandler.trigger(this._element, EVENT_HIDDEN$3);
      };
      this._queueCallback(completeCallback, this._element, true);
    }
    dispose() {
      this._backdrop.dispose();
      this._focustrap.deactivate();
      super.dispose();
    }

    // Private
    _initializeBackDrop() {
      const clickCallback = () => {
        if (this._config.backdrop === 'static') {
          EventHandler.trigger(this._element, EVENT_HIDE_PREVENTED);
          return;
        }
        this.hide();
      };

      // 'static' option will be translated to true, and booleans will keep their value
      const isVisible = Boolean(this._config.backdrop);
      return new Backdrop({
        className: CLASS_NAME_BACKDROP,
        isVisible,
        isAnimated: true,
        rootElement: this._element.parentNode,
        clickCallback: isVisible ? clickCallback : null
      });
    }
    _initializeFocusTrap() {
      return new FocusTrap({
        trapElement: this._element
      });
    }
    _addEventListeners() {
      EventHandler.on(this._element, EVENT_KEYDOWN_DISMISS, event => {
        if (event.key !== ESCAPE_KEY) {
          return;
        }
        if (this._config.keyboard) {
          this.hide();
          return;
        }
        EventHandler.trigger(this._element, EVENT_HIDE_PREVENTED);
      });
    }

    // Static
    static jQueryInterface(config) {
      return this.each(function () {
        const data = Offcanvas.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (data[config] === undefined || config.startsWith('_') || config === 'constructor') {
          throw new TypeError(`No method named "${config}"`);
        }
        data[config](this);
      });
    }
  }

  /**
   * Data API implementation
   */

  EventHandler.on(document, EVENT_CLICK_DATA_API$1, SELECTOR_DATA_TOGGLE$1, function (event) {
    const target = SelectorEngine.getElementFromSelector(this);
    if (['A', 'AREA'].includes(this.tagName)) {
      event.preventDefault();
    }
    if (isDisabled(this)) {
      return;
    }
    EventHandler.one(target, EVENT_HIDDEN$3, () => {
      // focus on trigger when it is closed
      if (isVisible(this)) {
        this.focus();
      }
    });

    // avoid conflict when clicking a toggler of an offcanvas, while another is open
    const alreadyOpen = SelectorEngine.findOne(OPEN_SELECTOR);
    if (alreadyOpen && alreadyOpen !== target) {
      Offcanvas.getInstance(alreadyOpen).hide();
    }
    const data = Offcanvas.getOrCreateInstance(target);
    data.toggle(this);
  });
  EventHandler.on(window, EVENT_LOAD_DATA_API$2, () => {
    for (const selector of SelectorEngine.find(OPEN_SELECTOR)) {
      Offcanvas.getOrCreateInstance(selector).show();
    }
  });
  EventHandler.on(window, EVENT_RESIZE, () => {
    for (const element of SelectorEngine.find('[aria-modal][class*=show][class*=offcanvas-]')) {
      if (getComputedStyle(element).position !== 'fixed') {
        Offcanvas.getOrCreateInstance(element).hide();
      }
    }
  });
  enableDismissTrigger(Offcanvas);

  /**
   * jQuery
   */

  defineJQueryPlugin(Offcanvas);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/sanitizer.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  // js-docs-start allow-list
  const ARIA_ATTRIBUTE_PATTERN = /^aria-[\w-]*$/i;
  const DefaultAllowlist = {
    // Global attributes allowed on any supplied element below.
    '*': ['class', 'dir', 'id', 'lang', 'role', ARIA_ATTRIBUTE_PATTERN],
    a: ['target', 'href', 'title', 'rel'],
    area: [],
    b: [],
    br: [],
    col: [],
    code: [],
    dd: [],
    div: [],
    dl: [],
    dt: [],
    em: [],
    hr: [],
    h1: [],
    h2: [],
    h3: [],
    h4: [],
    h5: [],
    h6: [],
    i: [],
    img: ['src', 'srcset', 'alt', 'title', 'width', 'height'],
    li: [],
    ol: [],
    p: [],
    pre: [],
    s: [],
    small: [],
    span: [],
    sub: [],
    sup: [],
    strong: [],
    u: [],
    ul: []
  };
  // js-docs-end allow-list

  const uriAttributes = new Set(['background', 'cite', 'href', 'itemtype', 'longdesc', 'poster', 'src', 'xlink:href']);

  /**
   * A pattern that recognizes URLs that are safe wrt. XSS in URL navigation
   * contexts.
   *
   * Shout-out to Angular https://github.com/angular/angular/blob/15.2.8/packages/core/src/sanitization/url_sanitizer.ts#L38
   */
  // eslint-disable-next-line unicorn/better-regex
  const SAFE_URL_PATTERN = /^(?!javascript:)(?:[a-z0-9+.-]+:|[^&:/?#]*(?:[/?#]|$))/i;
  const allowedAttribute = (attribute, allowedAttributeList) => {
    const attributeName = attribute.nodeName.toLowerCase();
    if (allowedAttributeList.includes(attributeName)) {
      if (uriAttributes.has(attributeName)) {
        return Boolean(SAFE_URL_PATTERN.test(attribute.nodeValue));
      }
      return true;
    }

    // Check if a regular expression validates the attribute.
    return allowedAttributeList.filter(attributeRegex => attributeRegex instanceof RegExp).some(regex => regex.test(attributeName));
  };
  function sanitizeHtml(unsafeHtml, allowList, sanitizeFunction) {
    if (!unsafeHtml.length) {
      return unsafeHtml;
    }
    if (sanitizeFunction && typeof sanitizeFunction === 'function') {
      return sanitizeFunction(unsafeHtml);
    }
    const domParser = new window.DOMParser();
    const createdDocument = domParser.parseFromString(unsafeHtml, 'text/html');
    const elements = [].concat(...createdDocument.body.querySelectorAll('*'));
    for (const element of elements) {
      const elementName = element.nodeName.toLowerCase();
      if (!Object.keys(allowList).includes(elementName)) {
        element.remove();
        continue;
      }
      const attributeList = [].concat(...element.attributes);
      const allowedAttributes = [].concat(allowList['*'] || [], allowList[elementName] || []);
      for (const attribute of attributeList) {
        if (!allowedAttribute(attribute, allowedAttributes)) {
          element.removeAttribute(attribute.nodeName);
        }
      }
    }
    return createdDocument.body.innerHTML;
  }

  /**
   * --------------------------------------------------------------------------
   * Bootstrap util/template-factory.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$5 = 'TemplateFactory';
  const Default$4 = {
    allowList: DefaultAllowlist,
    content: {},
    // { selector : text ,  selector2 : text2 , }
    extraClass: '',
    html: false,
    sanitize: true,
    sanitizeFn: null,
    template: '<div></div>'
  };
  const DefaultType$4 = {
    allowList: 'object',
    content: 'object',
    extraClass: '(string|function)',
    html: 'boolean',
    sanitize: 'boolean',
    sanitizeFn: '(null|function)',
    template: 'string'
  };
  const DefaultContentType = {
    entry: '(string|element|function|null)',
    selector: '(string|element)'
  };

  /**
   * Class definition
   */

  class TemplateFactory extends Config {
    constructor(config) {
      super();
      this._config = this._getConfig(config);
    }

    // Getters
    static get Default() {
      return Default$4;
    }
    static get DefaultType() {
      return DefaultType$4;
    }
    static get NAME() {
      return NAME$5;
    }

    // Public
    getContent() {
      return Object.values(this._config.content).map(config => this._resolvePossibleFunction(config)).filter(Boolean);
    }
    hasContent() {
      return this.getContent().length > 0;
    }
    changeContent(content) {
      this._checkContent(content);
      this._config.content = {
        ...this._config.content,
        ...content
      };
      return this;
    }
    toHtml() {
      const templateWrapper = document.createElement('div');
      templateWrapper.innerHTML = this._maybeSanitize(this._config.template);
      for (const [selector, text] of Object.entries(this._config.content)) {
        this._setContent(templateWrapper, text, selector);
      }
      const template = templateWrapper.children[0];
      const extraClass = this._resolvePossibleFunction(this._config.extraClass);
      if (extraClass) {
        template.classList.add(...extraClass.split(' '));
      }
      return template;
    }

    // Private
    _typeCheckConfig(config) {
      super._typeCheckConfig(config);
      this._checkContent(config.content);
    }
    _checkContent(arg) {
      for (const [selector, content] of Object.entries(arg)) {
        super._typeCheckConfig({
          selector,
          entry: content
        }, DefaultContentType);
      }
    }
    _setContent(template, content, selector) {
      const templateElement = SelectorEngine.findOne(selector, template);
      if (!templateElement) {
        return;
      }
      content = this._resolvePossibleFunction(content);
      if (!content) {
        templateElement.remove();
        return;
      }
      if (isElement(content)) {
        this._putElementInTemplate(getElement(content), templateElement);
        return;
      }
      if (this._config.html) {
        templateElement.innerHTML = this._maybeSanitize(content);
        return;
      }
      templateElement.textContent = content;
    }
    _maybeSanitize(arg) {
      return this._config.sanitize ? sanitizeHtml(arg, this._config.allowList, this._config.sanitizeFn) : arg;
    }
    _resolvePossibleFunction(arg) {
      return execute(arg, [this]);
    }
    _putElementInTemplate(element, templateElement) {
      if (this._config.html) {
        templateElement.innerHTML = '';
        templateElement.append(element);
        return;
      }
      templateElement.textContent = element.textContent;
    }
  }

  /**
   * --------------------------------------------------------------------------
   * Bootstrap tooltip.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$4 = 'tooltip';
  const DISALLOWED_ATTRIBUTES = new Set(['sanitize', 'allowList', 'sanitizeFn']);
  const CLASS_NAME_FADE$2 = 'fade';
  const CLASS_NAME_MODAL = 'modal';
  const CLASS_NAME_SHOW$2 = 'show';
  const SELECTOR_TOOLTIP_INNER = '.tooltip-inner';
  const SELECTOR_MODAL = `.${CLASS_NAME_MODAL}`;
  const EVENT_MODAL_HIDE = 'hide.bs.modal';
  const TRIGGER_HOVER = 'hover';
  const TRIGGER_FOCUS = 'focus';
  const TRIGGER_CLICK = 'click';
  const TRIGGER_MANUAL = 'manual';
  const EVENT_HIDE$2 = 'hide';
  const EVENT_HIDDEN$2 = 'hidden';
  const EVENT_SHOW$2 = 'show';
  const EVENT_SHOWN$2 = 'shown';
  const EVENT_INSERTED = 'inserted';
  const EVENT_CLICK$1 = 'click';
  const EVENT_FOCUSIN$1 = 'focusin';
  const EVENT_FOCUSOUT$1 = 'focusout';
  const EVENT_MOUSEENTER = 'mouseenter';
  const EVENT_MOUSELEAVE = 'mouseleave';
  const AttachmentMap = {
    AUTO: 'auto',
    TOP: 'top',
    RIGHT: isRTL() ? 'left' : 'right',
    BOTTOM: 'bottom',
    LEFT: isRTL() ? 'right' : 'left'
  };
  const Default$3 = {
    allowList: DefaultAllowlist,
    animation: true,
    boundary: 'clippingParents',
    container: false,
    customClass: '',
    delay: 0,
    fallbackPlacements: ['top', 'right', 'bottom', 'left'],
    html: false,
    offset: [0, 6],
    placement: 'top',
    popperConfig: null,
    sanitize: true,
    sanitizeFn: null,
    selector: false,
    template: '<div class="tooltip" role="tooltip">' + '<div class="tooltip-arrow"></div>' + '<div class="tooltip-inner"></div>' + '</div>',
    title: '',
    trigger: 'hover focus'
  };
  const DefaultType$3 = {
    allowList: 'object',
    animation: 'boolean',
    boundary: '(string|element)',
    container: '(string|element|boolean)',
    customClass: '(string|function)',
    delay: '(number|object)',
    fallbackPlacements: 'array',
    html: 'boolean',
    offset: '(array|string|function)',
    placement: '(string|function)',
    popperConfig: '(null|object|function)',
    sanitize: 'boolean',
    sanitizeFn: '(null|function)',
    selector: '(string|boolean)',
    template: 'string',
    title: '(string|element|function)',
    trigger: 'string'
  };

  /**
   * Class definition
   */

  class Tooltip extends BaseComponent {
    constructor(element, config) {
      if (typeof Popper__namespace === 'undefined') {
        throw new TypeError('Bootstrap\'s tooltips require Popper (https://popper.js.org)');
      }
      super(element, config);

      // Private
      this._isEnabled = true;
      this._timeout = 0;
      this._isHovered = null;
      this._activeTrigger = {};
      this._popper = null;
      this._templateFactory = null;
      this._newContent = null;

      // Protected
      this.tip = null;
      this._setListeners();
      if (!this._config.selector) {
        this._fixTitle();
      }
    }

    // Getters
    static get Default() {
      return Default$3;
    }
    static get DefaultType() {
      return DefaultType$3;
    }
    static get NAME() {
      return NAME$4;
    }

    // Public
    enable() {
      this._isEnabled = true;
    }
    disable() {
      this._isEnabled = false;
    }
    toggleEnabled() {
      this._isEnabled = !this._isEnabled;
    }
    toggle() {
      if (!this._isEnabled) {
        return;
      }
      this._activeTrigger.click = !this._activeTrigger.click;
      if (this._isShown()) {
        this._leave();
        return;
      }
      this._enter();
    }
    dispose() {
      clearTimeout(this._timeout);
      EventHandler.off(this._element.closest(SELECTOR_MODAL), EVENT_MODAL_HIDE, this._hideModalHandler);
      if (this._element.getAttribute('data-bs-original-title')) {
        this._element.setAttribute('title', this._element.getAttribute('data-bs-original-title'));
      }
      this._disposePopper();
      super.dispose();
    }
    show() {
      if (this._element.style.display === 'none') {
        throw new Error('Please use show on visible elements');
      }
      if (!(this._isWithContent() && this._isEnabled)) {
        return;
      }
      const showEvent = EventHandler.trigger(this._element, this.constructor.eventName(EVENT_SHOW$2));
      const shadowRoot = findShadowRoot(this._element);
      const isInTheDom = (shadowRoot || this._element.ownerDocument.documentElement).contains(this._element);
      if (showEvent.defaultPrevented || !isInTheDom) {
        return;
      }

      // TODO: v6 remove this or make it optional
      this._disposePopper();
      const tip = this._getTipElement();
      this._element.setAttribute('aria-describedby', tip.getAttribute('id'));
      const {
        container
      } = this._config;
      if (!this._element.ownerDocument.documentElement.contains(this.tip)) {
        container.append(tip);
        EventHandler.trigger(this._element, this.constructor.eventName(EVENT_INSERTED));
      }
      this._popper = this._createPopper(tip);
      tip.classList.add(CLASS_NAME_SHOW$2);

      // If this is a touch-enabled device we add extra
      // empty mouseover listeners to the body's immediate children;
      // only needed because of broken event delegation on iOS
      // https://www.quirksmode.org/blog/archives/2014/02/mouse_event_bub.html
      if ('ontouchstart' in document.documentElement) {
        for (const element of [].concat(...document.body.children)) {
          EventHandler.on(element, 'mouseover', noop);
        }
      }
      const complete = () => {
        EventHandler.trigger(this._element, this.constructor.eventName(EVENT_SHOWN$2));
        if (this._isHovered === false) {
          this._leave();
        }
        this._isHovered = false;
      };
      this._queueCallback(complete, this.tip, this._isAnimated());
    }
    hide() {
      if (!this._isShown()) {
        return;
      }
      const hideEvent = EventHandler.trigger(this._element, this.constructor.eventName(EVENT_HIDE$2));
      if (hideEvent.defaultPrevented) {
        return;
      }
      const tip = this._getTipElement();
      tip.classList.remove(CLASS_NAME_SHOW$2);

      // If this is a touch-enabled device we remove the extra
      // empty mouseover listeners we added for iOS support
      if ('ontouchstart' in document.documentElement) {
        for (const element of [].concat(...document.body.children)) {
          EventHandler.off(element, 'mouseover', noop);
        }
      }
      this._activeTrigger[TRIGGER_CLICK] = false;
      this._activeTrigger[TRIGGER_FOCUS] = false;
      this._activeTrigger[TRIGGER_HOVER] = false;
      this._isHovered = null; // it is a trick to support manual triggering

      const complete = () => {
        if (this._isWithActiveTrigger()) {
          return;
        }
        if (!this._isHovered) {
          this._disposePopper();
        }
        this._element.removeAttribute('aria-describedby');
        EventHandler.trigger(this._element, this.constructor.eventName(EVENT_HIDDEN$2));
      };
      this._queueCallback(complete, this.tip, this._isAnimated());
    }
    update() {
      if (this._popper) {
        this._popper.update();
      }
    }

    // Protected
    _isWithContent() {
      return Boolean(this._getTitle());
    }
    _getTipElement() {
      if (!this.tip) {
        this.tip = this._createTipElement(this._newContent || this._getContentForTemplate());
      }
      return this.tip;
    }
    _createTipElement(content) {
      const tip = this._getTemplateFactory(content).toHtml();

      // TODO: remove this check in v6
      if (!tip) {
        return null;
      }
      tip.classList.remove(CLASS_NAME_FADE$2, CLASS_NAME_SHOW$2);
      // TODO: v6 the following can be achieved with CSS only
      tip.classList.add(`bs-${this.constructor.NAME}-auto`);
      const tipId = getUID(this.constructor.NAME).toString();
      tip.setAttribute('id', tipId);
      if (this._isAnimated()) {
        tip.classList.add(CLASS_NAME_FADE$2);
      }
      return tip;
    }
    setContent(content) {
      this._newContent = content;
      if (this._isShown()) {
        this._disposePopper();
        this.show();
      }
    }
    _getTemplateFactory(content) {
      if (this._templateFactory) {
        this._templateFactory.changeContent(content);
      } else {
        this._templateFactory = new TemplateFactory({
          ...this._config,
          // the `content` var has to be after `this._config`
          // to override config.content in case of popover
          content,
          extraClass: this._resolvePossibleFunction(this._config.customClass)
        });
      }
      return this._templateFactory;
    }
    _getContentForTemplate() {
      return {
        [SELECTOR_TOOLTIP_INNER]: this._getTitle()
      };
    }
    _getTitle() {
      return this._resolvePossibleFunction(this._config.title) || this._element.getAttribute('data-bs-original-title');
    }

    // Private
    _initializeOnDelegatedTarget(event) {
      return this.constructor.getOrCreateInstance(event.delegateTarget, this._getDelegateConfig());
    }
    _isAnimated() {
      return this._config.animation || this.tip && this.tip.classList.contains(CLASS_NAME_FADE$2);
    }
    _isShown() {
      return this.tip && this.tip.classList.contains(CLASS_NAME_SHOW$2);
    }
    _createPopper(tip) {
      const placement = execute(this._config.placement, [this, tip, this._element]);
      const attachment = AttachmentMap[placement.toUpperCase()];
      return Popper__namespace.createPopper(this._element, tip, this._getPopperConfig(attachment));
    }
    _getOffset() {
      const {
        offset
      } = this._config;
      if (typeof offset === 'string') {
        return offset.split(',').map(value => Number.parseInt(value, 10));
      }
      if (typeof offset === 'function') {
        return popperData => offset(popperData, this._element);
      }
      return offset;
    }
    _resolvePossibleFunction(arg) {
      return execute(arg, [this._element]);
    }
    _getPopperConfig(attachment) {
      const defaultBsPopperConfig = {
        placement: attachment,
        modifiers: [{
          name: 'flip',
          options: {
            fallbackPlacements: this._config.fallbackPlacements
          }
        }, {
          name: 'offset',
          options: {
            offset: this._getOffset()
          }
        }, {
          name: 'preventOverflow',
          options: {
            boundary: this._config.boundary
          }
        }, {
          name: 'arrow',
          options: {
            element: `.${this.constructor.NAME}-arrow`
          }
        }, {
          name: 'preSetPlacement',
          enabled: true,
          phase: 'beforeMain',
          fn: data => {
            // Pre-set Popper's placement attribute in order to read the arrow sizes properly.
            // Otherwise, Popper mixes up the width and height dimensions since the initial arrow style is for top placement
            this._getTipElement().setAttribute('data-popper-placement', data.state.placement);
          }
        }]
      };
      return {
        ...defaultBsPopperConfig,
        ...execute(this._config.popperConfig, [defaultBsPopperConfig])
      };
    }
    _setListeners() {
      const triggers = this._config.trigger.split(' ');
      for (const trigger of triggers) {
        if (trigger === 'click') {
          EventHandler.on(this._element, this.constructor.eventName(EVENT_CLICK$1), this._config.selector, event => {
            const context = this._initializeOnDelegatedTarget(event);
            context.toggle();
          });
        } else if (trigger !== TRIGGER_MANUAL) {
          const eventIn = trigger === TRIGGER_HOVER ? this.constructor.eventName(EVENT_MOUSEENTER) : this.constructor.eventName(EVENT_FOCUSIN$1);
          const eventOut = trigger === TRIGGER_HOVER ? this.constructor.eventName(EVENT_MOUSELEAVE) : this.constructor.eventName(EVENT_FOCUSOUT$1);
          EventHandler.on(this._element, eventIn, this._config.selector, event => {
            const context = this._initializeOnDelegatedTarget(event);
            context._activeTrigger[event.type === 'focusin' ? TRIGGER_FOCUS : TRIGGER_HOVER] = true;
            context._enter();
          });
          EventHandler.on(this._element, eventOut, this._config.selector, event => {
            const context = this._initializeOnDelegatedTarget(event);
            context._activeTrigger[event.type === 'focusout' ? TRIGGER_FOCUS : TRIGGER_HOVER] = context._element.contains(event.relatedTarget);
            context._leave();
          });
        }
      }
      this._hideModalHandler = () => {
        if (this._element) {
          this.hide();
        }
      };
      EventHandler.on(this._element.closest(SELECTOR_MODAL), EVENT_MODAL_HIDE, this._hideModalHandler);
    }
    _fixTitle() {
      const title = this._element.getAttribute('title');
      if (!title) {
        return;
      }
      if (!this._element.getAttribute('aria-label') && !this._element.textContent.trim()) {
        this._element.setAttribute('aria-label', title);
      }
      this._element.setAttribute('data-bs-original-title', title); // DO NOT USE IT. Is only for backwards compatibility
      this._element.removeAttribute('title');
    }
    _enter() {
      if (this._isShown() || this._isHovered) {
        this._isHovered = true;
        return;
      }
      this._isHovered = true;
      this._setTimeout(() => {
        if (this._isHovered) {
          this.show();
        }
      }, this._config.delay.show);
    }
    _leave() {
      if (this._isWithActiveTrigger()) {
        return;
      }
      this._isHovered = false;
      this._setTimeout(() => {
        if (!this._isHovered) {
          this.hide();
        }
      }, this._config.delay.hide);
    }
    _setTimeout(handler, timeout) {
      clearTimeout(this._timeout);
      this._timeout = setTimeout(handler, timeout);
    }
    _isWithActiveTrigger() {
      return Object.values(this._activeTrigger).includes(true);
    }
    _getConfig(config) {
      const dataAttributes = Manipulator.getDataAttributes(this._element);
      for (const dataAttribute of Object.keys(dataAttributes)) {
        if (DISALLOWED_ATTRIBUTES.has(dataAttribute)) {
          delete dataAttributes[dataAttribute];
        }
      }
      config = {
        ...dataAttributes,
        ...(typeof config === 'object' && config ? config : {})
      };
      config = this._mergeConfigObj(config);
      config = this._configAfterMerge(config);
      this._typeCheckConfig(config);
      return config;
    }
    _configAfterMerge(config) {
      config.container = config.container === false ? document.body : getElement(config.container);
      if (typeof config.delay === 'number') {
        config.delay = {
          show: config.delay,
          hide: config.delay
        };
      }
      if (typeof config.title === 'number') {
        config.title = config.title.toString();
      }
      if (typeof config.content === 'number') {
        config.content = config.content.toString();
      }
      return config;
    }
    _getDelegateConfig() {
      const config = {};
      for (const [key, value] of Object.entries(this._config)) {
        if (this.constructor.Default[key] !== value) {
          config[key] = value;
        }
      }
      config.selector = false;
      config.trigger = 'manual';

      // In the future can be replaced with:
      // const keysWithDifferentValues = Object.entries(this._config).filter(entry => this.constructor.Default[entry[0]] !== this._config[entry[0]])
      // `Object.fromEntries(keysWithDifferentValues)`
      return config;
    }
    _disposePopper() {
      if (this._popper) {
        this._popper.destroy();
        this._popper = null;
      }
      if (this.tip) {
        this.tip.remove();
        this.tip = null;
      }
    }

    // Static
    static jQueryInterface(config) {
      return this.each(function () {
        const data = Tooltip.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (typeof data[config] === 'undefined') {
          throw new TypeError(`No method named "${config}"`);
        }
        data[config]();
      });
    }
  }

  /**
   * jQuery
   */

  defineJQueryPlugin(Tooltip);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap popover.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$3 = 'popover';
  const SELECTOR_TITLE = '.popover-header';
  const SELECTOR_CONTENT = '.popover-body';
  const Default$2 = {
    ...Tooltip.Default,
    content: '',
    offset: [0, 8],
    placement: 'right',
    template: '<div class="popover" role="tooltip">' + '<div class="popover-arrow"></div>' + '<h3 class="popover-header"></h3>' + '<div class="popover-body"></div>' + '</div>',
    trigger: 'click'
  };
  const DefaultType$2 = {
    ...Tooltip.DefaultType,
    content: '(null|string|element|function)'
  };

  /**
   * Class definition
   */

  class Popover extends Tooltip {
    // Getters
    static get Default() {
      return Default$2;
    }
    static get DefaultType() {
      return DefaultType$2;
    }
    static get NAME() {
      return NAME$3;
    }

    // Overrides
    _isWithContent() {
      return this._getTitle() || this._getContent();
    }

    // Private
    _getContentForTemplate() {
      return {
        [SELECTOR_TITLE]: this._getTitle(),
        [SELECTOR_CONTENT]: this._getContent()
      };
    }
    _getContent() {
      return this._resolvePossibleFunction(this._config.content);
    }

    // Static
    static jQueryInterface(config) {
      return this.each(function () {
        const data = Popover.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (typeof data[config] === 'undefined') {
          throw new TypeError(`No method named "${config}"`);
        }
        data[config]();
      });
    }
  }

  /**
   * jQuery
   */

  defineJQueryPlugin(Popover);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap scrollspy.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$2 = 'scrollspy';
  const DATA_KEY$2 = 'bs.scrollspy';
  const EVENT_KEY$2 = `.${DATA_KEY$2}`;
  const DATA_API_KEY = '.data-api';
  const EVENT_ACTIVATE = `activate${EVENT_KEY$2}`;
  const EVENT_CLICK = `click${EVENT_KEY$2}`;
  const EVENT_LOAD_DATA_API$1 = `load${EVENT_KEY$2}${DATA_API_KEY}`;
  const CLASS_NAME_DROPDOWN_ITEM = 'dropdown-item';
  const CLASS_NAME_ACTIVE$1 = 'active';
  const SELECTOR_DATA_SPY = '[data-bs-spy="scroll"]';
  const SELECTOR_TARGET_LINKS = '[href]';
  const SELECTOR_NAV_LIST_GROUP = '.nav, .list-group';
  const SELECTOR_NAV_LINKS = '.nav-link';
  const SELECTOR_NAV_ITEMS = '.nav-item';
  const SELECTOR_LIST_ITEMS = '.list-group-item';
  const SELECTOR_LINK_ITEMS = `${SELECTOR_NAV_LINKS}, ${SELECTOR_NAV_ITEMS} > ${SELECTOR_NAV_LINKS}, ${SELECTOR_LIST_ITEMS}`;
  const SELECTOR_DROPDOWN = '.dropdown';
  const SELECTOR_DROPDOWN_TOGGLE$1 = '.dropdown-toggle';
  const Default$1 = {
    offset: null,
    // TODO: v6 @deprecated, keep it for backwards compatibility reasons
    rootMargin: '0px 0px -25%',
    smoothScroll: false,
    target: null,
    threshold: [0.1, 0.5, 1]
  };
  const DefaultType$1 = {
    offset: '(number|null)',
    // TODO v6 @deprecated, keep it for backwards compatibility reasons
    rootMargin: 'string',
    smoothScroll: 'boolean',
    target: 'element',
    threshold: 'array'
  };

  /**
   * Class definition
   */

  class ScrollSpy extends BaseComponent {
    constructor(element, config) {
      super(element, config);

      // this._element is the observablesContainer and config.target the menu links wrapper
      this._targetLinks = new Map();
      this._observableSections = new Map();
      this._rootElement = getComputedStyle(this._element).overflowY === 'visible' ? null : this._element;
      this._activeTarget = null;
      this._observer = null;
      this._previousScrollData = {
        visibleEntryTop: 0,
        parentScrollTop: 0
      };
      this.refresh(); // initialize
    }

    // Getters
    static get Default() {
      return Default$1;
    }
    static get DefaultType() {
      return DefaultType$1;
    }
    static get NAME() {
      return NAME$2;
    }

    // Public
    refresh() {
      this._initializeTargetsAndObservables();
      this._maybeEnableSmoothScroll();
      if (this._observer) {
        this._observer.disconnect();
      } else {
        this._observer = this._getNewObserver();
      }
      for (const section of this._observableSections.values()) {
        this._observer.observe(section);
      }
    }
    dispose() {
      this._observer.disconnect();
      super.dispose();
    }

    // Private
    _configAfterMerge(config) {
      // TODO: on v6 target should be given explicitly & remove the {target: 'ss-target'} case
      config.target = getElement(config.target) || document.body;

      // TODO: v6 Only for backwards compatibility reasons. Use rootMargin only
      config.rootMargin = config.offset ? `${config.offset}px 0px -30%` : config.rootMargin;
      if (typeof config.threshold === 'string') {
        config.threshold = config.threshold.split(',').map(value => Number.parseFloat(value));
      }
      return config;
    }
    _maybeEnableSmoothScroll() {
      if (!this._config.smoothScroll) {
        return;
      }

      // unregister any previous listeners
      EventHandler.off(this._config.target, EVENT_CLICK);
      EventHandler.on(this._config.target, EVENT_CLICK, SELECTOR_TARGET_LINKS, event => {
        const observableSection = this._observableSections.get(event.target.hash);
        if (observableSection) {
          event.preventDefault();
          const root = this._rootElement || window;
          const height = observableSection.offsetTop - this._element.offsetTop;
          if (root.scrollTo) {
            root.scrollTo({
              top: height,
              behavior: 'smooth'
            });
            return;
          }

          // Chrome 60 doesn't support `scrollTo`
          root.scrollTop = height;
        }
      });
    }
    _getNewObserver() {
      const options = {
        root: this._rootElement,
        threshold: this._config.threshold,
        rootMargin: this._config.rootMargin
      };
      return new IntersectionObserver(entries => this._observerCallback(entries), options);
    }

    // The logic of selection
    _observerCallback(entries) {
      const targetElement = entry => this._targetLinks.get(`#${entry.target.id}`);
      const activate = entry => {
        this._previousScrollData.visibleEntryTop = entry.target.offsetTop;
        this._process(targetElement(entry));
      };
      const parentScrollTop = (this._rootElement || document.documentElement).scrollTop;
      const userScrollsDown = parentScrollTop >= this._previousScrollData.parentScrollTop;
      this._previousScrollData.parentScrollTop = parentScrollTop;
      for (const entry of entries) {
        if (!entry.isIntersecting) {
          this._activeTarget = null;
          this._clearActiveClass(targetElement(entry));
          continue;
        }
        const entryIsLowerThanPrevious = entry.target.offsetTop >= this._previousScrollData.visibleEntryTop;
        // if we are scrolling down, pick the bigger offsetTop
        if (userScrollsDown && entryIsLowerThanPrevious) {
          activate(entry);
          // if parent isn't scrolled, let's keep the first visible item, breaking the iteration
          if (!parentScrollTop) {
            return;
          }
          continue;
        }

        // if we are scrolling up, pick the smallest offsetTop
        if (!userScrollsDown && !entryIsLowerThanPrevious) {
          activate(entry);
        }
      }
    }
    _initializeTargetsAndObservables() {
      this._targetLinks = new Map();
      this._observableSections = new Map();
      const targetLinks = SelectorEngine.find(SELECTOR_TARGET_LINKS, this._config.target);
      for (const anchor of targetLinks) {
        // ensure that the anchor has an id and is not disabled
        if (!anchor.hash || isDisabled(anchor)) {
          continue;
        }
        const observableSection = SelectorEngine.findOne(decodeURI(anchor.hash), this._element);

        // ensure that the observableSection exists & is visible
        if (isVisible(observableSection)) {
          this._targetLinks.set(decodeURI(anchor.hash), anchor);
          this._observableSections.set(anchor.hash, observableSection);
        }
      }
    }
    _process(target) {
      if (this._activeTarget === target) {
        return;
      }
      this._clearActiveClass(this._config.target);
      this._activeTarget = target;
      target.classList.add(CLASS_NAME_ACTIVE$1);
      this._activateParents(target);
      EventHandler.trigger(this._element, EVENT_ACTIVATE, {
        relatedTarget: target
      });
    }
    _activateParents(target) {
      // Activate dropdown parents
      if (target.classList.contains(CLASS_NAME_DROPDOWN_ITEM)) {
        SelectorEngine.findOne(SELECTOR_DROPDOWN_TOGGLE$1, target.closest(SELECTOR_DROPDOWN)).classList.add(CLASS_NAME_ACTIVE$1);
        return;
      }
      for (const listGroup of SelectorEngine.parents(target, SELECTOR_NAV_LIST_GROUP)) {
        // Set triggered links parents as active
        // With both <ul> and <nav> markup a parent is the previous sibling of any nav ancestor
        for (const item of SelectorEngine.prev(listGroup, SELECTOR_LINK_ITEMS)) {
          item.classList.add(CLASS_NAME_ACTIVE$1);
        }
      }
    }
    _clearActiveClass(parent) {
      parent.classList.remove(CLASS_NAME_ACTIVE$1);
      const activeNodes = SelectorEngine.find(`${SELECTOR_TARGET_LINKS}.${CLASS_NAME_ACTIVE$1}`, parent);
      for (const node of activeNodes) {
        node.classList.remove(CLASS_NAME_ACTIVE$1);
      }
    }

    // Static
    static jQueryInterface(config) {
      return this.each(function () {
        const data = ScrollSpy.getOrCreateInstance(this, config);
        if (typeof config !== 'string') {
          return;
        }
        if (data[config] === undefined || config.startsWith('_') || config === 'constructor') {
          throw new TypeError(`No method named "${config}"`);
        }
        data[config]();
      });
    }
  }

  /**
   * Data API implementation
   */

  EventHandler.on(window, EVENT_LOAD_DATA_API$1, () => {
    for (const spy of SelectorEngine.find(SELECTOR_DATA_SPY)) {
      ScrollSpy.getOrCreateInstance(spy);
    }
  });

  /**
   * jQuery
   */

  defineJQueryPlugin(ScrollSpy);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap tab.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME$1 = 'tab';
  const DATA_KEY$1 = 'bs.tab';
  const EVENT_KEY$1 = `.${DATA_KEY$1}`;
  const EVENT_HIDE$1 = `hide${EVENT_KEY$1}`;
  const EVENT_HIDDEN$1 = `hidden${EVENT_KEY$1}`;
  const EVENT_SHOW$1 = `show${EVENT_KEY$1}`;
  const EVENT_SHOWN$1 = `shown${EVENT_KEY$1}`;
  const EVENT_CLICK_DATA_API = `click${EVENT_KEY$1}`;
  const EVENT_KEYDOWN = `keydown${EVENT_KEY$1}`;
  const EVENT_LOAD_DATA_API = `load${EVENT_KEY$1}`;
  const ARROW_LEFT_KEY = 'ArrowLeft';
  const ARROW_RIGHT_KEY = 'ArrowRight';
  const ARROW_UP_KEY = 'ArrowUp';
  const ARROW_DOWN_KEY = 'ArrowDown';
  const HOME_KEY = 'Home';
  const END_KEY = 'End';
  const CLASS_NAME_ACTIVE = 'active';
  const CLASS_NAME_FADE$1 = 'fade';
  const CLASS_NAME_SHOW$1 = 'show';
  const CLASS_DROPDOWN = 'dropdown';
  const SELECTOR_DROPDOWN_TOGGLE = '.dropdown-toggle';
  const SELECTOR_DROPDOWN_MENU = '.dropdown-menu';
  const NOT_SELECTOR_DROPDOWN_TOGGLE = `:not(${SELECTOR_DROPDOWN_TOGGLE})`;
  const SELECTOR_TAB_PANEL = '.list-group, .nav, [role="tablist"]';
  const SELECTOR_OUTER = '.nav-item, .list-group-item';
  const SELECTOR_INNER = `.nav-link${NOT_SELECTOR_DROPDOWN_TOGGLE}, .list-group-item${NOT_SELECTOR_DROPDOWN_TOGGLE}, [role="tab"]${NOT_SELECTOR_DROPDOWN_TOGGLE}`;
  const SELECTOR_DATA_TOGGLE = '[data-bs-toggle="tab"], [data-bs-toggle="pill"], [data-bs-toggle="list"]'; // TODO: could only be `tab` in v6
  const SELECTOR_INNER_ELEM = `${SELECTOR_INNER}, ${SELECTOR_DATA_TOGGLE}`;
  const SELECTOR_DATA_TOGGLE_ACTIVE = `.${CLASS_NAME_ACTIVE}[data-bs-toggle="tab"], .${CLASS_NAME_ACTIVE}[data-bs-toggle="pill"], .${CLASS_NAME_ACTIVE}[data-bs-toggle="list"]`;

  /**
   * Class definition
   */

  class Tab extends BaseComponent {
    constructor(element) {
      super(element);
      this._parent = this._element.closest(SELECTOR_TAB_PANEL);
      if (!this._parent) {
        return;
        // TODO: should throw exception in v6
        // throw new TypeError(`${element.outerHTML} has not a valid parent ${SELECTOR_INNER_ELEM}`)
      }

      // Set up initial aria attributes
      this._setInitialAttributes(this._parent, this._getChildren());
      EventHandler.on(this._element, EVENT_KEYDOWN, event => this._keydown(event));
    }

    // Getters
    static get NAME() {
      return NAME$1;
    }

    // Public
    show() {
      // Shows this elem and deactivate the active sibling if exists
      const innerElem = this._element;
      if (this._elemIsActive(innerElem)) {
        return;
      }

      // Search for active tab on same parent to deactivate it
      const active = this._getActiveElem();
      const hideEvent = active ? EventHandler.trigger(active, EVENT_HIDE$1, {
        relatedTarget: innerElem
      }) : null;
      const showEvent = EventHandler.trigger(innerElem, EVENT_SHOW$1, {
        relatedTarget: active
      });
      if (showEvent.defaultPrevented || hideEvent && hideEvent.defaultPrevented) {
        return;
      }
      this._deactivate(active, innerElem);
      this._activate(innerElem, active);
    }

    // Private
    _activate(element, relatedElem) {
      if (!element) {
        return;
      }
      element.classList.add(CLASS_NAME_ACTIVE);
      this._activate(SelectorEngine.getElementFromSelector(element)); // Search and activate/show the proper section

      const complete = () => {
        if (element.getAttribute('role') !== 'tab') {
          element.classList.add(CLASS_NAME_SHOW$1);
          return;
        }
        element.removeAttribute('tabindex');
        element.setAttribute('aria-selected', true);
        this._toggleDropDown(element, true);
        EventHandler.trigger(element, EVENT_SHOWN$1, {
          relatedTarget: relatedElem
        });
      };
      this._queueCallback(complete, element, element.classList.contains(CLASS_NAME_FADE$1));
    }
    _deactivate(element, relatedElem) {
      if (!element) {
        return;
      }
      element.classList.remove(CLASS_NAME_ACTIVE);
      element.blur();
      this._deactivate(SelectorEngine.getElementFromSelector(element)); // Search and deactivate the shown section too

      const complete = () => {
        if (element.getAttribute('role') !== 'tab') {
          element.classList.remove(CLASS_NAME_SHOW$1);
          return;
        }
        element.setAttribute('aria-selected', false);
        element.setAttribute('tabindex', '-1');
        this._toggleDropDown(element, false);
        EventHandler.trigger(element, EVENT_HIDDEN$1, {
          relatedTarget: relatedElem
        });
      };
      this._queueCallback(complete, element, element.classList.contains(CLASS_NAME_FADE$1));
    }
    _keydown(event) {
      if (![ARROW_LEFT_KEY, ARROW_RIGHT_KEY, ARROW_UP_KEY, ARROW_DOWN_KEY, HOME_KEY, END_KEY].includes(event.key)) {
        return;
      }
      event.stopPropagation(); // stopPropagation/preventDefault both added to support up/down keys without scrolling the page
      event.preventDefault();
      const children = this._getChildren().filter(element => !isDisabled(element));
      let nextActiveElement;
      if ([HOME_KEY, END_KEY].includes(event.key)) {
        nextActiveElement = children[event.key === HOME_KEY ? 0 : children.length - 1];
      } else {
        const isNext = [ARROW_RIGHT_KEY, ARROW_DOWN_KEY].includes(event.key);
        nextActiveElement = getNextActiveElement(children, event.target, isNext, true);
      }
      if (nextActiveElement) {
        nextActiveElement.focus({
          preventScroll: true
        });
        Tab.getOrCreateInstance(nextActiveElement).show();
      }
    }
    _getChildren() {
      // collection of inner elements
      return SelectorEngine.find(SELECTOR_INNER_ELEM, this._parent);
    }
    _getActiveElem() {
      return this._getChildren().find(child => this._elemIsActive(child)) || null;
    }
    _setInitialAttributes(parent, children) {
      this._setAttributeIfNotExists(parent, 'role', 'tablist');
      for (const child of children) {
        this._setInitialAttributesOnChild(child);
      }
    }
    _setInitialAttributesOnChild(child) {
      child = this._getInnerElement(child);
      const isActive = this._elemIsActive(child);
      const outerElem = this._getOuterElement(child);
      child.setAttribute('aria-selected', isActive);
      if (outerElem !== child) {
        this._setAttributeIfNotExists(outerElem, 'role', 'presentation');
      }
      if (!isActive) {
        child.setAttribute('tabindex', '-1');
      }
      this._setAttributeIfNotExists(child, 'role', 'tab');

      // set attributes to the related panel too
      this._setInitialAttributesOnTargetPanel(child);
    }
    _setInitialAttributesOnTargetPanel(child) {
      const target = SelectorEngine.getElementFromSelector(child);
      if (!target) {
        return;
      }
      this._setAttributeIfNotExists(target, 'role', 'tabpanel');
      if (child.id) {
        this._setAttributeIfNotExists(target, 'aria-labelledby', `${child.id}`);
      }
    }
    _toggleDropDown(element, open) {
      const outerElem = this._getOuterElement(element);
      if (!outerElem.classList.contains(CLASS_DROPDOWN)) {
        return;
      }
      const toggle = (selector, className) => {
        const element = SelectorEngine.findOne(selector, outerElem);
        if (element) {
          element.classList.toggle(className, open);
        }
      };
      toggle(SELECTOR_DROPDOWN_TOGGLE, CLASS_NAME_ACTIVE);
      toggle(SELECTOR_DROPDOWN_MENU, CLASS_NAME_SHOW$1);
      outerElem.setAttribute('aria-expanded', open);
    }
    _setAttributeIfNotExists(element, attribute, value) {
      if (!element.hasAttribute(attribute)) {
        element.setAttribute(attribute, value);
      }
    }
    _elemIsActive(elem) {
      return elem.classList.contains(CLASS_NAME_ACTIVE);
    }

    // Try to get the inner element (usually the .nav-link)
    _getInnerElement(elem) {
      return elem.matches(SELECTOR_INNER_ELEM) ? elem : SelectorEngine.findOne(SELECTOR_INNER_ELEM, elem);
    }

    // Try to get the outer element (usually the .nav-item)
    _getOuterElement(elem) {
      return elem.closest(SELECTOR_OUTER) || elem;
    }

    // Static
    static jQueryInterface(config) {
      return this.each(function () {
        const data = Tab.getOrCreateInstance(this);
        if (typeof config !== 'string') {
          return;
        }
        if (data[config] === undefined || config.startsWith('_') || config === 'constructor') {
          throw new TypeError(`No method named "${config}"`);
        }
        data[config]();
      });
    }
  }

  /**
   * Data API implementation
   */

  EventHandler.on(document, EVENT_CLICK_DATA_API, SELECTOR_DATA_TOGGLE, function (event) {
    if (['A', 'AREA'].includes(this.tagName)) {
      event.preventDefault();
    }
    if (isDisabled(this)) {
      return;
    }
    Tab.getOrCreateInstance(this).show();
  });

  /**
   * Initialize on focus
   */
  EventHandler.on(window, EVENT_LOAD_DATA_API, () => {
    for (const element of SelectorEngine.find(SELECTOR_DATA_TOGGLE_ACTIVE)) {
      Tab.getOrCreateInstance(element);
    }
  });
  /**
   * jQuery
   */

  defineJQueryPlugin(Tab);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap toast.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */


  /**
   * Constants
   */

  const NAME = 'toast';
  const DATA_KEY = 'bs.toast';
  const EVENT_KEY = `.${DATA_KEY}`;
  const EVENT_MOUSEOVER = `mouseover${EVENT_KEY}`;
  const EVENT_MOUSEOUT = `mouseout${EVENT_KEY}`;
  const EVENT_FOCUSIN = `focusin${EVENT_KEY}`;
  const EVENT_FOCUSOUT = `focusout${EVENT_KEY}`;
  const EVENT_HIDE = `hide${EVENT_KEY}`;
  const EVENT_HIDDEN = `hidden${EVENT_KEY}`;
  const EVENT_SHOW = `show${EVENT_KEY}`;
  const EVENT_SHOWN = `shown${EVENT_KEY}`;
  const CLASS_NAME_FADE = 'fade';
  const CLASS_NAME_HIDE = 'hide'; // @deprecated - kept here only for backwards compatibility
  const CLASS_NAME_SHOW = 'show';
  const CLASS_NAME_SHOWING = 'showing';
  const DefaultType = {
    animation: 'boolean',
    autohide: 'boolean',
    delay: 'number'
  };
  const Default = {
    animation: true,
    autohide: true,
    delay: 5000
  };

  /**
   * Class definition
   */

  class Toast extends BaseComponent {
    constructor(element, config) {
      super(element, config);
      this._timeout = null;
      this._hasMouseInteraction = false;
      this._hasKeyboardInteraction = false;
      this._setListeners();
    }

    // Getters
    static get Default() {
      return Default;
    }
    static get DefaultType() {
      return DefaultType;
    }
    static get NAME() {
      return NAME;
    }

    // Public
    show() {
      const showEvent = EventHandler.trigger(this._element, EVENT_SHOW);
      if (showEvent.defaultPrevented) {
        return;
      }
      this._clearTimeout();
      if (this._config.animation) {
        this._element.classList.add(CLASS_NAME_FADE);
      }
      const complete = () => {
        this._element.classList.remove(CLASS_NAME_SHOWING);
        EventHandler.trigger(this._element, EVENT_SHOWN);
        this._maybeScheduleHide();
      };
      this._element.classList.remove(CLASS_NAME_HIDE); // @deprecated
      reflow(this._element);
      this._element.classList.add(CLASS_NAME_SHOW, CLASS_NAME_SHOWING);
      this._queueCallback(complete, this._element, this._config.animation);
    }
    hide() {
      if (!this.isShown()) {
        return;
      }
      const hideEvent = EventHandler.trigger(this._element, EVENT_HIDE);
      if (hideEvent.defaultPrevented) {
        return;
      }
      const complete = () => {
        this._element.classList.add(CLASS_NAME_HIDE); // @deprecated
        this._element.classList.remove(CLASS_NAME_SHOWING, CLASS_NAME_SHOW);
        EventHandler.trigger(this._element, EVENT_HIDDEN);
      };
      this._element.classList.add(CLASS_NAME_SHOWING);
      this._queueCallback(complete, this._element, this._config.animation);
    }
    dispose() {
      this._clearTimeout();
      if (this.isShown()) {
        this._element.classList.remove(CLASS_NAME_SHOW);
      }
      super.dispose();
    }
    isShown() {
      return this._element.classList.contains(CLASS_NAME_SHOW);
    }

    // Private

    _maybeScheduleHide() {
      if (!this._config.autohide) {
        return;
      }
      if (this._hasMouseInteraction || this._hasKeyboardInteraction) {
        return;
      }
      this._timeout = setTimeout(() => {
        this.hide();
      }, this._config.delay);
    }
    _onInteraction(event, isInteracting) {
      switch (event.type) {
        case 'mouseover':
        case 'mouseout':
          {
            this._hasMouseInteraction = isInteracting;
            break;
          }
        case 'focusin':
        case 'focusout':
          {
            this._hasKeyboardInteraction = isInteracting;
            break;
          }
      }
      if (isInteracting) {
        this._clearTimeout();
        return;
      }
      const nextElement = event.relatedTarget;
      if (this._element === nextElement || this._element.contains(nextElement)) {
        return;
      }
      this._maybeScheduleHide();
    }
    _setListeners() {
      EventHandler.on(this._element, EVENT_MOUSEOVER, event => this._onInteraction(event, true));
      EventHandler.on(this._element, EVENT_MOUSEOUT, event => this._onInteraction(event, false));
      EventHandler.on(this._element, EVENT_FOCUSIN, event => this._onInteraction(event, true));
      EventHandler.on(this._element, EVENT_FOCUSOUT, event => this._onInteraction(event, false));
    }
    _clearTimeout() {
      clearTimeout(this._timeout);
      this._timeout = null;
    }

    // Static
    static jQueryInterface(config) {
      return this.each(function () {
        const data = Toast.getOrCreateInstance(this, config);
        if (typeof config === 'string') {
          if (typeof data[config] === 'undefined') {
            throw new TypeError(`No method named "${config}"`);
          }
          data[config](this);
        }
      });
    }
  }

  /**
   * Data API implementation
   */

  enableDismissTrigger(Toast);

  /**
   * jQuery
   */

  defineJQueryPlugin(Toast);

  /**
   * --------------------------------------------------------------------------
   * Bootstrap index.umd.js
   * Licensed under MIT (https://github.com/twbs/bootstrap/blob/main/LICENSE)
   * --------------------------------------------------------------------------
   */

  const index_umd = {
    Alert,
    Button,
    Carousel,
    Collapse,
    Dropdown,
    Modal,
    Offcanvas,
    Popover,
    ScrollSpy,
    Tab,
    Toast,
    Tooltip
  };

  return index_umd;

}));


var tns=function(){var t=window,Ai=t.requestAnimationFrame||t.webkitRequestAnimationFrame||t.mozRequestAnimationFrame||t.msRequestAnimationFrame||function(t){return setTimeout(t,16)},e=window,Ni=e.cancelAnimationFrame||e.mozCancelAnimationFrame||function(t){clearTimeout(t)};function Li(){for(var t,e,n,i=arguments[0]||{},a=1,r=arguments.length;a<r;a++)if(null!==(t=arguments[a]))for(e in t)i!==(n=t[e])&&void 0!==n&&(i[e]=n);return i}function Bi(t){return 0<=["true","false"].indexOf(t)?JSON.parse(t):t}function Si(t,e,n,i){if(i)try{t.setItem(e,n)}catch(t){}return n}function Hi(){var t=document,e=t.body;return e||((e=t.createElement("body")).fake=!0),e}var n=document.documentElement;function Oi(t){var e="";return t.fake&&(e=n.style.overflow,t.style.background="",t.style.overflow=n.style.overflow="hidden",n.appendChild(t)),e}function Di(t,e){t.fake&&(t.remove(),n.style.overflow=e,n.offsetHeight)}function ki(t,e,n,i){"insertRule"in t?t.insertRule(e+"{"+n+"}",i):t.addRule(e,n,i)}function Ri(t){return("insertRule"in t?t.cssRules:t.rules).length}function Ii(t,e,n){for(var i=0,a=t.length;i<a;i++)e.call(n,t[i],i)}var i="classList"in document.createElement("_"),Pi=i?function(t,e){return t.classList.contains(e)}:function(t,e){return 0<=t.className.indexOf(e)},zi=i?function(t,e){Pi(t,e)||t.classList.add(e)}:function(t,e){Pi(t,e)||(t.className+=" "+e)},Wi=i?function(t,e){Pi(t,e)&&t.classList.remove(e)}:function(t,e){Pi(t,e)&&(t.className=t.className.replace(e,""))};function qi(t,e){return t.hasAttribute(e)}function Fi(t,e){return t.getAttribute(e)}function r(t){return void 0!==t.item}function ji(t,e){if(t=r(t)||t instanceof Array?t:[t],"[object Object]"===Object.prototype.toString.call(e))for(var n=t.length;n--;)for(var i in e)t[n].setAttribute(i,e[i])}function Vi(t,e){t=r(t)||t instanceof Array?t:[t];for(var n=(e=e instanceof Array?e:[e]).length,i=t.length;i--;)for(var a=n;a--;)t[i].removeAttribute(e[a])}function Gi(t){for(var e=[],n=0,i=t.length;n<i;n++)e.push(t[n]);return e}function Qi(t,e){"none"!==t.style.display&&(t.style.display="none")}function Xi(t,e){"none"===t.style.display&&(t.style.display="")}function Yi(t){return"none"!==window.getComputedStyle(t).display}function Ki(e){if("string"==typeof e){var n=[e],i=e.charAt(0).toUpperCase()+e.substr(1);["Webkit","Moz","ms","O"].forEach(function(t){"ms"===t&&"transform"!==e||n.push(t+i)}),e=n}for(var t=document.createElement("fakeelement"),a=(e.length,0);a<e.length;a++){var r=e[a];if(void 0!==t.style[r])return r}return!1}function Ji(t,e){var n=!1;return/^Webkit/.test(t)?n="webkit"+e+"End":/^O/.test(t)?n="o"+e+"End":t&&(n=e.toLowerCase()+"end"),n}var a=!1;try{var o=Object.defineProperty({},"passive",{get:function(){a=!0}});window.addEventListener("test",null,o)}catch(t){}var u=!!a&&{passive:!0};function Ui(t,e,n){for(var i in e){var a=0<=["touchstart","touchmove"].indexOf(i)&&!n&&u;t.addEventListener(i,e[i],a)}}function _i(t,e){for(var n in e){var i=0<=["touchstart","touchmove"].indexOf(n)&&u;t.removeEventListener(n,e[n],i)}}function Zi(){return{topics:{},on:function(t,e){this.topics[t]=this.topics[t]||[],this.topics[t].push(e)},off:function(t,e){if(this.topics[t])for(var n=0;n<this.topics[t].length;n++)if(this.topics[t][n]===e){this.topics[t].splice(n,1);break}},emit:function(e,n){n.type=e,this.topics[e]&&this.topics[e].forEach(function(t){t(n,e)})}}}Object.keys||(Object.keys=function(t){var e=[];for(var n in t)Object.prototype.hasOwnProperty.call(t,n)&&e.push(n);return e}),"remove"in Element.prototype||(Element.prototype.remove=function(){this.parentNode&&this.parentNode.removeChild(this)});var $i=function(H){H=Li({container:".slider",mode:"carousel",axis:"horizontal",items:1,gutter:0,edgePadding:0,fixedWidth:!1,autoWidth:!1,viewportMax:!1,slideBy:1,center:!1,controls:!0,controlsPosition:"top",controlsText:["prev","next"],controlsContainer:!1,prevButton:!1,nextButton:!1,nav:!0,navPosition:"top",navContainer:!1,navAsThumbnails:!1,arrowKeys:!1,speed:300,autoplay:!1,autoplayPosition:"top",autoplayTimeout:5e3,autoplayDirection:"forward",autoplayText:["start","stop"],autoplayHoverPause:!1,autoplayButton:!1,autoplayButtonOutput:!0,autoplayResetOnVisibility:!0,animateIn:"tns-fadeIn",animateOut:"tns-fadeOut",animateNormal:"tns-normal",animateDelay:!1,loop:!0,rewind:!1,autoHeight:!1,responsive:!1,lazyload:!1,lazyloadSelector:".tns-lazy-img",touch:!0,mouseDrag:!1,swipeAngle:15,nested:!1,preventActionWhenRunning:!1,preventScrollOnTouch:!1,freezable:!0,onInit:!1,useLocalStorage:!0,nonce:!1},H||{});var O=document,m=window,a={ENTER:13,SPACE:32,LEFT:37,RIGHT:39},e={},n=H.useLocalStorage;if(n){var t=navigator.userAgent,i=new Date;try{(e=m.localStorage)?(e.setItem(i,i),n=e.getItem(i)==i,e.removeItem(i)):n=!1,n||(e={})}catch(t){n=!1}n&&(e.tnsApp&&e.tnsApp!==t&&["tC","tPL","tMQ","tTf","t3D","tTDu","tTDe","tADu","tADe","tTE","tAE"].forEach(function(t){e.removeItem(t)}),localStorage.tnsApp=t)}var y=e.tC?Bi(e.tC):Si(e,"tC",function(){var t=document,e=Hi(),n=Oi(e),i=t.createElement("div"),a=!1;e.appendChild(i);try{for(var r,o="(10px * 10)",u=["calc"+o,"-moz-calc"+o,"-webkit-calc"+o],l=0;l<3;l++)if(r=u[l],i.style.width=r,100===i.offsetWidth){a=r.replace(o,"");break}}catch(t){}return e.fake?Di(e,n):i.remove(),a}(),n),g=e.tPL?Bi(e.tPL):Si(e,"tPL",function(){var t,e=document,n=Hi(),i=Oi(n),a=e.createElement("div"),r=e.createElement("div"),o="";a.className="tns-t-subp2",r.className="tns-t-ct";for(var u=0;u<70;u++)o+="<div></div>";return r.innerHTML=o,a.appendChild(r),n.appendChild(a),t=Math.abs(a.getBoundingClientRect().left-r.children[67].getBoundingClientRect().left)<2,n.fake?Di(n,i):a.remove(),t}(),n),D=e.tMQ?Bi(e.tMQ):Si(e,"tMQ",function(){if(window.matchMedia||window.msMatchMedia)return!0;var t,e=document,n=Hi(),i=Oi(n),a=e.createElement("div"),r=e.createElement("style"),o="@media all and (min-width:1px){.tns-mq-test{position:absolute}}";return r.type="text/css",a.className="tns-mq-test",n.appendChild(r),n.appendChild(a),r.styleSheet?r.styleSheet.cssText=o:r.appendChild(e.createTextNode(o)),t=window.getComputedStyle?window.getComputedStyle(a).position:a.currentStyle.position,n.fake?Di(n,i):a.remove(),"absolute"===t}(),n),r=e.tTf?Bi(e.tTf):Si(e,"tTf",Ki("transform"),n),o=e.t3D?Bi(e.t3D):Si(e,"t3D",function(t){if(!t)return!1;if(!window.getComputedStyle)return!1;var e,n=document,i=Hi(),a=Oi(i),r=n.createElement("p"),o=9<t.length?"-"+t.slice(0,-9).toLowerCase()+"-":"";return o+="transform",i.insertBefore(r,null),r.style[t]="translate3d(1px,1px,1px)",e=window.getComputedStyle(r).getPropertyValue(o),i.fake?Di(i,a):r.remove(),void 0!==e&&0<e.length&&"none"!==e}(r),n),x=e.tTDu?Bi(e.tTDu):Si(e,"tTDu",Ki("transitionDuration"),n),u=e.tTDe?Bi(e.tTDe):Si(e,"tTDe",Ki("transitionDelay"),n),b=e.tADu?Bi(e.tADu):Si(e,"tADu",Ki("animationDuration"),n),l=e.tADe?Bi(e.tADe):Si(e,"tADe",Ki("animationDelay"),n),s=e.tTE?Bi(e.tTE):Si(e,"tTE",Ji(x,"Transition"),n),c=e.tAE?Bi(e.tAE):Si(e,"tAE",Ji(b,"Animation"),n),f=m.console&&"function"==typeof m.console.warn,d=["container","controlsContainer","prevButton","nextButton","navContainer","autoplayButton"],v={};if(d.forEach(function(t){if("string"==typeof H[t]){var e=H[t],n=O.querySelector(e);if(v[t]=e,!n||!n.nodeName)return void(f&&console.warn("Can't find",H[t]));H[t]=n}}),!(H.container.children.length<1)){var k=H.responsive,R=H.nested,I="carousel"===H.mode;if(k){0 in k&&(H=Li(H,k[0]),delete k[0]);var p={};for(var h in k){var w=k[h];w="number"==typeof w?{items:w}:w,p[h]=w}k=p,p=null}if(I||function t(e){for(var n in e)I||("slideBy"===n&&(e[n]="page"),"edgePadding"===n&&(e[n]=!1),"autoHeight"===n&&(e[n]=!1)),"responsive"===n&&t(e[n])}(H),!I){H.axis="horizontal",H.slideBy="page",H.edgePadding=!1;var P=H.animateIn,z=H.animateOut,C=H.animateDelay,W=H.animateNormal}var M,q,F="horizontal"===H.axis,T=O.createElement("div"),j=O.createElement("div"),V=H.container,E=V.parentNode,A=V.outerHTML,G=V.children,Q=G.length,X=rn(),Y=!1;k&&En(),I&&(V.className+=" tns-vpfix");var N,L,B,S,K,J,U,_,Z,$=H.autoWidth,tt=sn("fixedWidth"),et=sn("edgePadding"),nt=sn("gutter"),it=un(),at=sn("center"),rt=$?1:Math.floor(sn("items")),ot=sn("slideBy"),ut=H.viewportMax||H.fixedWidthViewportWidth,lt=sn("arrowKeys"),st=sn("speed"),ct=H.rewind,ft=!ct&&H.loop,dt=sn("autoHeight"),vt=sn("controls"),pt=sn("controlsText"),ht=sn("nav"),mt=sn("touch"),yt=sn("mouseDrag"),gt=sn("autoplay"),xt=sn("autoplayTimeout"),bt=sn("autoplayText"),wt=sn("autoplayHoverPause"),Ct=sn("autoplayResetOnVisibility"),Mt=(U=null,_=sn("nonce"),Z=document.createElement("style"),U&&Z.setAttribute("media",U),_&&Z.setAttribute("nonce",_),document.querySelector("head").appendChild(Z),Z.sheet?Z.sheet:Z.styleSheet),Tt=H.lazyload,Et=H.lazyloadSelector,At=[],Nt=ft?(K=function(){{if($||tt&&!ut)return Q-1;var t=tt?"fixedWidth":"items",e=[];if((tt||H[t]<Q)&&e.push(H[t]),k)for(var n in k){var i=k[n][t];i&&(tt||i<Q)&&e.push(i)}return e.length||e.push(0),Math.ceil(tt?ut/Math.min.apply(null,e):Math.max.apply(null,e))}}(),J=I?Math.ceil((5*K-Q)/2):4*K-Q,J=Math.max(K,J),ln("edgePadding")?J+1:J):0,Lt=I?Q+2*Nt:Q+Nt,Bt=!(!tt&&!$||ft),St=tt?_n():null,Ht=!I||!ft,Ot=F?"left":"top",Dt="",kt="",Rt=tt?function(){return at&&!ft?Q-1:Math.ceil(-St/(tt+nt))}:$?function(){for(var t=0;t<Lt;t++)if(N[t]>=-St)return t}:function(){return at&&I&&!ft?Q-1:ft||I?Math.max(0,Lt-Math.ceil(rt)):Lt-1},It=en(sn("startIndex")),Pt=It,zt=(tn(),0),Wt=$?null:Rt(),qt=H.preventActionWhenRunning,Ft=H.swipeAngle,jt=!Ft||"?",Vt=!1,Gt=H.onInit,Qt=new Zi,Xt=" tns-slider tns-"+H.mode,Yt=V.id||(S=window.tnsId,window.tnsId=S?S+1:1,"tns"+window.tnsId),Kt=sn("disable"),Jt=!1,Ut=H.freezable,_t=!(!Ut||$)&&Tn(),Zt=!1,$t={click:oi,keydown:function(t){t=pi(t);var e=[a.LEFT,a.RIGHT].indexOf(t.keyCode);0<=e&&(0===e?we.disabled||oi(t,-1):Ce.disabled||oi(t,1))}},te={click:function(t){if(Vt){if(qt)return;ai()}var e=hi(t=pi(t));for(;e!==Ae&&!qi(e,"data-nav");)e=e.parentNode;if(qi(e,"data-nav")){var n=Se=Number(Fi(e,"data-nav")),i=tt||$?n*Q/Le:n*rt,a=le?n:Math.min(Math.ceil(i),Q-1);ri(a,t),He===n&&(Pe&&fi(),Se=-1)}},keydown:function(t){t=pi(t);var e=O.activeElement;if(!qi(e,"data-nav"))return;var n=[a.LEFT,a.RIGHT,a.ENTER,a.SPACE].indexOf(t.keyCode),i=Number(Fi(e,"data-nav"));0<=n&&(0===n?0<i&&vi(Ee[i-1]):1===n?i<Le-1&&vi(Ee[i+1]):ri(Se=i,t))}},ee={mouseover:function(){Pe&&(li(),ze=!0)},mouseout:function(){ze&&(ui(),ze=!1)}},ne={visibilitychange:function(){O.hidden?Pe&&(li(),qe=!0):qe&&(ui(),qe=!1)}},ie={keydown:function(t){t=pi(t);var e=[a.LEFT,a.RIGHT].indexOf(t.keyCode);0<=e&&oi(t,0===e?-1:1)}},ae={touchstart:xi,touchmove:bi,touchend:wi,touchcancel:wi},re={mousedown:xi,mousemove:bi,mouseup:wi,mouseleave:wi},oe=ln("controls"),ue=ln("nav"),le=!!$||H.navAsThumbnails,se=ln("autoplay"),ce=ln("touch"),fe=ln("mouseDrag"),de="tns-slide-active",ve="tns-slide-cloned",pe="tns-complete",he={load:function(t){kn(hi(t))},error:function(t){e=hi(t),zi(e,"failed"),Rn(e);var e}},me="force"===H.preventScrollOnTouch;if(oe)var ye,ge,xe=H.controlsContainer,be=H.controlsContainer?H.controlsContainer.outerHTML:"",we=H.prevButton,Ce=H.nextButton,Me=H.prevButton?H.prevButton.outerHTML:"",Te=H.nextButton?H.nextButton.outerHTML:"";if(ue)var Ee,Ae=H.navContainer,Ne=H.navContainer?H.navContainer.outerHTML:"",Le=$?Q:Mi(),Be=0,Se=-1,He=an(),Oe=He,De="tns-nav-active",ke="Carousel Page ",Re=" (Current Slide)";if(se)var Ie,Pe,ze,We,qe,Fe="forward"===H.autoplayDirection?1:-1,je=H.autoplayButton,Ve=H.autoplayButton?H.autoplayButton.outerHTML:"",Ge=["<span class='tns-visually-hidden'>"," animation</span>"];if(ce||fe)var Qe,Xe,Ye={},Ke={},Je=!1,Ue=F?function(t,e){return t.x-e.x}:function(t,e){return t.y-e.y};$||$e(Kt||_t),r&&(Ot=r,Dt="translate",o?(Dt+=F?"3d(":"3d(0px, ",kt=F?", 0px, 0px)":", 0px)"):(Dt+=F?"X(":"Y(",kt=")")),I&&(V.className=V.className.replace("tns-vpfix","")),function(){ln("gutter");T.className="tns-outer",j.className="tns-inner",T.id=Yt+"-ow",j.id=Yt+"-iw",""===V.id&&(V.id=Yt);Xt+=g||$?" tns-subpixel":" tns-no-subpixel",Xt+=y?" tns-calc":" tns-no-calc",$&&(Xt+=" tns-autowidth");Xt+=" tns-"+H.axis,V.className+=Xt,I?((M=O.createElement("div")).id=Yt+"-mw",M.className="tns-ovh",T.appendChild(M),M.appendChild(j)):T.appendChild(j);if(dt){var t=M||j;t.className+=" tns-ah"}if(E.insertBefore(T,V),j.appendChild(V),Ii(G,function(t,e){zi(t,"tns-item"),t.id||(t.id=Yt+"-item"+e),!I&&W&&zi(t,W),ji(t,{"aria-hidden":"true",tabindex:"-1"})}),Nt){for(var e=O.createDocumentFragment(),n=O.createDocumentFragment(),i=Nt;i--;){var a=i%Q,r=G[a].cloneNode(!0);if(zi(r,ve),Vi(r,"id"),n.insertBefore(r,n.firstChild),I){var o=G[Q-1-a].cloneNode(!0);zi(o,ve),Vi(o,"id"),e.appendChild(o)}}V.insertBefore(e,V.firstChild),V.appendChild(n),G=V.children}}(),function(){if(!I)for(var t=It,e=It+Math.min(Q,rt);t<e;t++){var n=G[t];n.style.left=100*(t-It)/rt+"%",zi(n,P),Wi(n,W)}F&&(g||$?(ki(Mt,"#"+Yt+" > .tns-item","font-size:"+m.getComputedStyle(G[0]).fontSize+";",Ri(Mt)),ki(Mt,"#"+Yt,"font-size:0;",Ri(Mt))):I&&Ii(G,function(t,e){var n;t.style.marginLeft=(n=e,y?y+"("+100*n+"% / "+Lt+")":100*n/Lt+"%")}));if(D){if(x){var i=M&&H.autoHeight?hn(H.speed):"";ki(Mt,"#"+Yt+"-mw",i,Ri(Mt))}i=cn(H.edgePadding,H.gutter,H.fixedWidth,H.speed,H.autoHeight),ki(Mt,"#"+Yt+"-iw",i,Ri(Mt)),I&&(i=F&&!$?"width:"+fn(H.fixedWidth,H.gutter,H.items)+";":"",x&&(i+=hn(st)),ki(Mt,"#"+Yt,i,Ri(Mt))),i=F&&!$?dn(H.fixedWidth,H.gutter,H.items):"",H.gutter&&(i+=vn(H.gutter)),I||(x&&(i+=hn(st)),b&&(i+=mn(st))),i&&ki(Mt,"#"+Yt+" > .tns-item",i,Ri(Mt))}else{I&&dt&&(M.style[x]=st/1e3+"s"),j.style.cssText=cn(et,nt,tt,dt),I&&F&&!$&&(V.style.width=fn(tt,nt,rt));var i=F&&!$?dn(tt,nt,rt):"";nt&&(i+=vn(nt)),i&&ki(Mt,"#"+Yt+" > .tns-item",i,Ri(Mt))}if(k&&D)for(var a in k){a=parseInt(a);var r=k[a],i="",o="",u="",l="",s="",c=$?null:sn("items",a),f=sn("fixedWidth",a),d=sn("speed",a),v=sn("edgePadding",a),p=sn("autoHeight",a),h=sn("gutter",a);x&&M&&sn("autoHeight",a)&&"speed"in r&&(o="#"+Yt+"-mw{"+hn(d)+"}"),("edgePadding"in r||"gutter"in r)&&(u="#"+Yt+"-iw{"+cn(v,h,f,d,p)+"}"),I&&F&&!$&&("fixedWidth"in r||"items"in r||tt&&"gutter"in r)&&(l="width:"+fn(f,h,c)+";"),x&&"speed"in r&&(l+=hn(d)),l&&(l="#"+Yt+"{"+l+"}"),("fixedWidth"in r||tt&&"gutter"in r||!I&&"items"in r)&&(s+=dn(f,h,c)),"gutter"in r&&(s+=vn(h)),!I&&"speed"in r&&(x&&(s+=hn(d)),b&&(s+=mn(d))),s&&(s="#"+Yt+" > .tns-item{"+s+"}"),(i=o+u+l+s)&&Mt.insertRule("@media (min-width: "+a/16+"em) {"+i+"}",Mt.cssRules.length)}}(),yn();var _e=ft?I?function(){var t=zt,e=Wt;t+=ot,e-=ot,et?(t+=1,e-=1):tt&&(it+nt)%(tt+nt)&&(e-=1),Nt&&(e<It?It-=Q:It<t&&(It+=Q))}:function(){if(Wt<It)for(;zt+Q<=It;)It-=Q;else if(It<zt)for(;It<=Wt-Q;)It+=Q}:function(){It=Math.max(zt,Math.min(Wt,It))},Ze=I?function(){var e,n,i,a,t,r,o,u,l,s,c;Jn(V,""),x||!st?(ti(),st&&Yi(V)||ai()):(e=V,n=Ot,i=Dt,a=kt,t=Zn(),r=st,o=ai,u=Math.min(r,10),l=0<=t.indexOf("%")?"%":"px",t=t.replace(l,""),s=Number(e.style[n].replace(i,"").replace(a,"").replace(l,"")),c=(t-s)/r*u,setTimeout(function t(){r-=u,s+=c,e.style[n]=i+s+l+a,0<r?setTimeout(t,u):o()},u)),F||Ci()}:function(){At=[];var t={};t[s]=t[c]=ai,_i(G[Pt],t),Ui(G[It],t),ei(Pt,P,z,!0),ei(It,W,P),s&&c&&st&&Yi(V)||ai()};return{version:"2.9.4",getInfo:Ei,events:Qt,goTo:ri,play:function(){gt&&!Pe&&(ci(),We=!1)},pause:function(){Pe&&(fi(),We=!0)},isOn:Y,updateSliderHeight:Fn,refresh:yn,destroy:function(){if(Mt.disabled=!0,Mt.ownerNode&&Mt.ownerNode.remove(),_i(m,{resize:Cn}),lt&&_i(O,ie),xe&&_i(xe,$t),Ae&&_i(Ae,te),_i(V,ee),_i(V,ne),je&&_i(je,{click:di}),gt&&clearInterval(Ie),I&&s){var t={};t[s]=ai,_i(V,t)}mt&&_i(V,ae),yt&&_i(V,re);var r=[A,be,Me,Te,Ne,Ve];for(var e in d.forEach(function(t,e){var n="container"===t?T:H[t];if("object"==typeof n&&n){var i=!!n.previousElementSibling&&n.previousElementSibling,a=n.parentNode;n.outerHTML=r[e],H[t]=i?i.nextElementSibling:a.firstElementChild}}),d=P=z=C=W=F=T=j=V=E=A=G=Q=q=X=$=tt=et=nt=it=rt=ot=ut=lt=st=ct=ft=dt=Mt=Tt=N=At=Nt=Lt=Bt=St=Ht=Ot=Dt=kt=Rt=It=Pt=zt=Wt=Ft=jt=Vt=Gt=Qt=Xt=Yt=Kt=Jt=Ut=_t=Zt=$t=te=ee=ne=ie=ae=re=oe=ue=le=se=ce=fe=de=pe=he=L=vt=pt=xe=be=we=Ce=ye=ge=ht=Ae=Ne=Ee=Le=Be=Se=He=Oe=De=ke=Re=gt=xt=Fe=bt=wt=je=Ve=Ct=Ge=Ie=Pe=ze=We=qe=Ye=Ke=Qe=Je=Xe=Ue=mt=yt=null,this)"rebuild"!==e&&(this[e]=null);Y=!1},rebuild:function(){return $i(Li(H,v))}}}function $e(t){t&&(vt=ht=mt=yt=lt=gt=wt=Ct=!1)}function tn(){for(var t=I?It-Nt:It;t<0;)t+=Q;return t%Q+1}function en(t){return t=t?Math.max(0,Math.min(ft?Q-1:Q-rt,t)):0,I?t+Nt:t}function nn(t){for(null==t&&(t=It),I&&(t-=Nt);t<0;)t+=Q;return Math.floor(t%Q)}function an(){var t,e=nn();return t=le?e:tt||$?Math.ceil((e+1)*Le/Q-1):Math.floor(e/rt),!ft&&I&&It===Wt&&(t=Le-1),t}function rn(){return m.innerWidth||O.documentElement.clientWidth||O.body.clientWidth}function on(t){return"top"===t?"afterbegin":"beforeend"}function un(){var t=et?2*et-nt:0;return function t(e){if(null!=e){var n,i,a=O.createElement("div");return e.appendChild(a),i=(n=a.getBoundingClientRect()).right-n.left,a.remove(),i||t(e.parentNode)}}(E)-t}function ln(t){if(H[t])return!0;if(k)for(var e in k)if(k[e][t])return!0;return!1}function sn(t,e){if(null==e&&(e=X),"items"===t&&tt)return Math.floor((it+nt)/(tt+nt))||1;var n=H[t];if(k)for(var i in k)e>=parseInt(i)&&t in k[i]&&(n=k[i][t]);return"slideBy"===t&&"page"===n&&(n=sn("items")),I||"slideBy"!==t&&"items"!==t||(n=Math.floor(n)),n}function cn(t,e,n,i,a){var r="";if(void 0!==t){var o=t;e&&(o-=e),r=F?"margin: 0 "+o+"px 0 "+t+"px;":"margin: "+t+"px 0 "+o+"px 0;"}else if(e&&!n){var u="-"+e+"px";r="margin: 0 "+(F?u+" 0 0":"0 "+u+" 0")+";"}return!I&&a&&x&&i&&(r+=hn(i)),r}function fn(t,e,n){return t?(t+e)*Lt+"px":y?y+"("+100*Lt+"% / "+n+")":100*Lt/n+"%"}function dn(t,e,n){var i;if(t)i=t+e+"px";else{I||(n=Math.floor(n));var a=I?Lt:n;i=y?y+"(100% / "+a+")":100/a+"%"}return i="width:"+i,"inner"!==R?i+";":i+" !important;"}function vn(t){var e="";!1!==t&&(e=(F?"padding-":"margin-")+(F?"right":"bottom")+": "+t+"px;");return e}function pn(t,e){var n=t.substring(0,t.length-e).toLowerCase();return n&&(n="-"+n+"-"),n}function hn(t){return pn(x,18)+"transition-duration:"+t/1e3+"s;"}function mn(t){return pn(b,17)+"animation-duration:"+t/1e3+"s;"}function yn(){if(ln("autoHeight")||$||!F){var t=V.querySelectorAll("img");Ii(t,function(t){var e=t.src;Tt||(e&&e.indexOf("data:image")<0?(t.src="",Ui(t,he),zi(t,"loading"),t.src=e):kn(t))}),Ai(function(){zn(Gi(t),function(){L=!0})}),ln("autoHeight")&&(t=In(It,Math.min(It+rt-1,Lt-1))),Tt?gn():Ai(function(){zn(Gi(t),gn)})}else I&&$n(),bn(),wn()}function gn(){if($&&1<Q){var i=ft?It:Q-1;!function t(){var e=G[i].getBoundingClientRect().left,n=G[i-1].getBoundingClientRect().right;Math.abs(e-n)<=1?xn():setTimeout(function(){t()},16)}()}else xn()}function xn(){F&&!$||(jn(),$?(St=_n(),Ut&&(_t=Tn()),Wt=Rt(),$e(Kt||_t)):Ci()),I&&$n(),bn(),wn()}function bn(){if(Vn(),T.insertAdjacentHTML("afterbegin",'<div class="tns-liveregion tns-visually-hidden" aria-live="polite" aria-atomic="true">slide <span class="current">'+Hn()+"</span>  of "+Q+"</div>"),B=T.querySelector(".tns-liveregion .current"),se){var t=gt?"stop":"start";je?ji(je,{"data-action":t}):H.autoplayButtonOutput&&(T.insertAdjacentHTML(on(H.autoplayPosition),'<button type="button" data-action="'+t+'">'+Ge[0]+t+Ge[1]+bt[0]+"</button>"),je=T.querySelector("[data-action]")),je&&Ui(je,{click:di}),gt&&(ci(),wt&&Ui(V,ee),Ct&&Ui(V,ne))}if(ue){if(Ae)ji(Ae,{"aria-label":"Carousel Pagination"}),Ii(Ee=Ae.children,function(t,e){ji(t,{"data-nav":e,tabindex:"-1","aria-label":ke+(e+1),"aria-controls":Yt})});else{for(var e="",n=le?"":'style="display:none"',i=0;i<Q;i++)e+='<button type="button" data-nav="'+i+'" tabindex="-1" aria-controls="'+Yt+'" '+n+' aria-label="'+ke+(i+1)+'"></button>';e='<div class="tns-nav" aria-label="Carousel Pagination">'+e+"</div>",T.insertAdjacentHTML(on(H.navPosition),e),Ae=T.querySelector(".tns-nav"),Ee=Ae.children}if(Ti(),x){var a=x.substring(0,x.length-18).toLowerCase(),r="transition: all "+st/1e3+"s";a&&(r="-"+a+"-"+r),ki(Mt,"[aria-controls^="+Yt+"-item]",r,Ri(Mt))}ji(Ee[He],{"aria-label":ke+(He+1)+Re}),Vi(Ee[He],"tabindex"),zi(Ee[He],De),Ui(Ae,te)}oe&&(xe||we&&Ce||(T.insertAdjacentHTML(on(H.controlsPosition),'<div class="tns-controls" aria-label="Carousel Navigation" tabindex="0"><button type="button" data-controls="prev" tabindex="-1" aria-controls="'+Yt+'">'+pt[0]+'</button><button type="button" data-controls="next" tabindex="-1" aria-controls="'+Yt+'">'+pt[1]+"</button></div>"),xe=T.querySelector(".tns-controls")),we&&Ce||(we=xe.children[0],Ce=xe.children[1]),H.controlsContainer&&ji(xe,{"aria-label":"Carousel Navigation",tabindex:"0"}),(H.controlsContainer||H.prevButton&&H.nextButton)&&ji([we,Ce],{"aria-controls":Yt,tabindex:"-1"}),(H.controlsContainer||H.prevButton&&H.nextButton)&&(ji(we,{"data-controls":"prev"}),ji(Ce,{"data-controls":"next"})),ye=Qn(we),ge=Qn(Ce),Kn(),xe?Ui(xe,$t):(Ui(we,$t),Ui(Ce,$t))),An()}function wn(){if(I&&s){var t={};t[s]=ai,Ui(V,t)}mt&&Ui(V,ae,H.preventScrollOnTouch),yt&&Ui(V,re),lt&&Ui(O,ie),"inner"===R?Qt.on("outerResized",function(){Mn(),Qt.emit("innerLoaded",Ei())}):(k||tt||$||dt||!F)&&Ui(m,{resize:Cn}),dt&&("outer"===R?Qt.on("innerLoaded",Pn):Kt||Pn()),Dn(),Kt?Bn():_t&&Ln(),Qt.on("indexChanged",Wn),"inner"===R&&Qt.emit("innerLoaded",Ei()),"function"==typeof Gt&&Gt(Ei()),Y=!0}function Cn(t){Ai(function(){Mn(pi(t))})}function Mn(t){if(Y){"outer"===R&&Qt.emit("outerResized",Ei(t)),X=rn();var e,n=q,i=!1;k&&(En(),(e=n!==q)&&Qt.emit("newBreakpointStart",Ei(t)));var a,r,o,u,l=rt,s=Kt,c=_t,f=lt,d=vt,v=ht,p=mt,h=yt,m=gt,y=wt,g=Ct,x=It;if(e){var b=tt,w=dt,C=pt,M=at,T=bt;if(!D)var E=nt,A=et}if(lt=sn("arrowKeys"),vt=sn("controls"),ht=sn("nav"),mt=sn("touch"),at=sn("center"),yt=sn("mouseDrag"),gt=sn("autoplay"),wt=sn("autoplayHoverPause"),Ct=sn("autoplayResetOnVisibility"),e&&(Kt=sn("disable"),tt=sn("fixedWidth"),st=sn("speed"),dt=sn("autoHeight"),pt=sn("controlsText"),bt=sn("autoplayText"),xt=sn("autoplayTimeout"),D||(et=sn("edgePadding"),nt=sn("gutter"))),$e(Kt),it=un(),F&&!$||Kt||(jn(),F||(Ci(),i=!0)),(tt||$)&&(St=_n(),Wt=Rt()),(e||tt)&&(rt=sn("items"),ot=sn("slideBy"),(r=rt!==l)&&(tt||$||(Wt=Rt()),_e())),e&&Kt!==s&&(Kt?Bn():function(){if(!Jt)return;if(Mt.disabled=!1,V.className+=Xt,$n(),ft)for(var t=Nt;t--;)I&&Xi(G[t]),Xi(G[Lt-t-1]);if(!I)for(var e=It,n=It+Q;e<n;e++){var i=G[e],a=e<It+rt?P:W;i.style.left=100*(e-It)/rt+"%",zi(i,a)}Nn(),Jt=!1}()),Ut&&(e||tt||$)&&(_t=Tn())!==c&&(_t?(ti(Zn(en(0))),Ln()):(!function(){if(!Zt)return;et&&D&&(j.style.margin="");if(Nt)for(var t="tns-transparent",e=Nt;e--;)I&&Wi(G[e],t),Wi(G[Lt-e-1],t);Nn(),Zt=!1}(),i=!0)),$e(Kt||_t),gt||(wt=Ct=!1),lt!==f&&(lt?Ui(O,ie):_i(O,ie)),vt!==d&&(vt?xe?Xi(xe):(we&&Xi(we),Ce&&Xi(Ce)):xe?Qi(xe):(we&&Qi(we),Ce&&Qi(Ce))),ht!==v&&(ht?(Xi(Ae),Ti()):Qi(Ae)),mt!==p&&(mt?Ui(V,ae,H.preventScrollOnTouch):_i(V,ae)),yt!==h&&(yt?Ui(V,re):_i(V,re)),gt!==m&&(gt?(je&&Xi(je),Pe||We||ci()):(je&&Qi(je),Pe&&fi())),wt!==y&&(wt?Ui(V,ee):_i(V,ee)),Ct!==g&&(Ct?Ui(O,ne):_i(O,ne)),e){if(tt===b&&at===M||(i=!0),dt!==w&&(dt||(j.style.height="")),vt&&pt!==C&&(we.innerHTML=pt[0],Ce.innerHTML=pt[1]),je&&bt!==T){var N=gt?1:0,L=je.innerHTML,B=L.length-T[N].length;L.substring(B)===T[N]&&(je.innerHTML=L.substring(0,B)+bt[N])}}else at&&(tt||$)&&(i=!0);if((r||tt&&!$)&&(Le=Mi(),Ti()),(a=It!==x)?(Qt.emit("indexChanged",Ei()),i=!0):r?a||Wn():(tt||$)&&(Dn(),Vn(),Sn()),r&&!I&&function(){for(var t=It+Math.min(Q,rt),e=Lt;e--;){var n=G[e];It<=e&&e<t?(zi(n,"tns-moving"),n.style.left=100*(e-It)/rt+"%",zi(n,P),Wi(n,W)):n.style.left&&(n.style.left="",zi(n,W),Wi(n,P)),Wi(n,z)}setTimeout(function(){Ii(G,function(t){Wi(t,"tns-moving")})},300)}(),!Kt&&!_t){if(e&&!D&&(et===A&&nt===E||(j.style.cssText=cn(et,nt,tt,st,dt)),F)){I&&(V.style.width=fn(tt,nt,rt));var S=dn(tt,nt,rt)+vn(nt);u=Ri(o=Mt)-1,"deleteRule"in o?o.deleteRule(u):o.removeRule(u),ki(Mt,"#"+Yt+" > .tns-item",S,Ri(Mt))}dt&&Pn(),i&&($n(),Pt=It)}e&&Qt.emit("newBreakpointEnd",Ei(t))}}function Tn(){if(!tt&&!$)return Q<=(at?rt-(rt-1)/2:rt);var t=tt?(tt+nt)*Q:N[Q],e=et?it+2*et:it+nt;return at&&(e-=tt?(it-tt)/2:(it-(N[It+1]-N[It]-nt))/2),t<=e}function En(){for(var t in q=0,k)(t=parseInt(t))<=X&&(q=t)}function An(){!gt&&je&&Qi(je),!ht&&Ae&&Qi(Ae),vt||(xe?Qi(xe):(we&&Qi(we),Ce&&Qi(Ce)))}function Nn(){gt&&je&&Xi(je),ht&&Ae&&Xi(Ae),vt&&(xe?Xi(xe):(we&&Xi(we),Ce&&Xi(Ce)))}function Ln(){if(!Zt){if(et&&(j.style.margin="0px"),Nt)for(var t="tns-transparent",e=Nt;e--;)I&&zi(G[e],t),zi(G[Lt-e-1],t);An(),Zt=!0}}function Bn(){if(!Jt){if(Mt.disabled=!0,V.className=V.className.replace(Xt.substring(1),""),Vi(V,["style"]),ft)for(var t=Nt;t--;)I&&Qi(G[t]),Qi(G[Lt-t-1]);if(F&&I||Vi(j,["style"]),!I)for(var e=It,n=It+Q;e<n;e++){var i=G[e];Vi(i,["style"]),Wi(i,P),Wi(i,W)}An(),Jt=!0}}function Sn(){var t=Hn();B.innerHTML!==t&&(B.innerHTML=t)}function Hn(){var t=On(),e=t[0]+1,n=t[1]+1;return e===n?e+"":e+" to "+n}function On(t){null==t&&(t=Zn());var n,i,a,r=It;if(at||et?($||tt)&&(i=-(parseFloat(t)+et),a=i+it+2*et):$&&(i=N[It],a=i+it),$)N.forEach(function(t,e){e<Lt&&((at||et)&&t<=i+.5&&(r=e),.5<=a-t&&(n=e))});else{if(tt){var e=tt+nt;at||et?(r=Math.floor(i/e),n=Math.ceil(a/e-1)):n=r+Math.ceil(it/e)-1}else if(at||et){var o=rt-1;if(at?(r-=o/2,n=It+o/2):n=It+o,et){var u=et*rt/it;r-=u,n+=u}r=Math.floor(r),n=Math.ceil(n)}else n=r+rt-1;r=Math.max(r,0),n=Math.min(n,Lt-1)}return[r,n]}function Dn(){if(Tt&&!Kt){var t=On();t.push(Et),In.apply(null,t).forEach(function(t){if(!Pi(t,pe)){var e={};e[s]=function(t){t.stopPropagation()},Ui(t,e),Ui(t,he),t.src=Fi(t,"data-src");var n=Fi(t,"data-srcset");n&&(t.srcset=n),zi(t,"loading")}})}}function kn(t){zi(t,"loaded"),Rn(t)}function Rn(t){zi(t,pe),Wi(t,"loading"),_i(t,he)}function In(t,e,n){var i=[];for(n||(n="img");t<=e;)Ii(G[t].querySelectorAll(n),function(t){i.push(t)}),t++;return i}function Pn(){var t=In.apply(null,On());Ai(function(){zn(t,Fn)})}function zn(n,t){return L?t():(n.forEach(function(t,e){!Tt&&t.complete&&Rn(t),Pi(t,pe)&&n.splice(e,1)}),n.length?void Ai(function(){zn(n,t)}):t())}function Wn(){Dn(),Vn(),Sn(),Kn(),function(){if(ht&&(He=0<=Se?Se:an(),Se=-1,He!==Oe)){var t=Ee[Oe],e=Ee[He];ji(t,{tabindex:"-1","aria-label":ke+(Oe+1)}),Wi(t,De),ji(e,{"aria-label":ke+(He+1)+Re}),Vi(e,"tabindex"),zi(e,De),Oe=He}}()}function qn(t,e){for(var n=[],i=t,a=Math.min(t+e,Lt);i<a;i++)n.push(G[i].offsetHeight);return Math.max.apply(null,n)}function Fn(){var t=dt?qn(It,rt):qn(Nt,Q),e=M||j;e.style.height!==t&&(e.style.height=t+"px")}function jn(){N=[0];var n=F?"left":"top",i=F?"right":"bottom",a=G[0].getBoundingClientRect()[n];Ii(G,function(t,e){e&&N.push(t.getBoundingClientRect()[n]-a),e===Lt-1&&N.push(t.getBoundingClientRect()[i]-a)})}function Vn(){var t=On(),n=t[0],i=t[1];Ii(G,function(t,e){n<=e&&e<=i?qi(t,"aria-hidden")&&(Vi(t,["aria-hidden","tabindex"]),zi(t,de)):qi(t,"aria-hidden")||(ji(t,{"aria-hidden":"true",tabindex:"-1"}),Wi(t,de))})}function Gn(t){return t.nodeName.toLowerCase()}function Qn(t){return"button"===Gn(t)}function Xn(t){return"true"===t.getAttribute("aria-disabled")}function Yn(t,e,n){t?e.disabled=n:e.setAttribute("aria-disabled",n.toString())}function Kn(){if(vt&&!ct&&!ft){var t=ye?we.disabled:Xn(we),e=ge?Ce.disabled:Xn(Ce),n=It<=zt,i=!ct&&Wt<=It;n&&!t&&Yn(ye,we,!0),!n&&t&&Yn(ye,we,!1),i&&!e&&Yn(ge,Ce,!0),!i&&e&&Yn(ge,Ce,!1)}}function Jn(t,e){x&&(t.style[x]=e)}function Un(t){return null==t&&(t=It),$?(it-(et?nt:0)-(N[t+1]-N[t]-nt))/2:tt?(it-tt)/2:(rt-1)/2}function _n(){var t=it+(et?nt:0)-(tt?(tt+nt)*Lt:N[Lt]);return at&&!ft&&(t=tt?-(tt+nt)*(Lt-1)-Un():Un(Lt-1)-N[Lt-1]),0<t&&(t=0),t}function Zn(t){var e;if(null==t&&(t=It),F&&!$)if(tt)e=-(tt+nt)*t,at&&(e+=Un());else{var n=r?Lt:rt;at&&(t-=Un()),e=100*-t/n}else e=-N[t],at&&$&&(e+=Un());return Bt&&(e=Math.max(e,St)),e+=!F||$||tt?"px":"%"}function $n(t){Jn(V,"0s"),ti(t)}function ti(t){null==t&&(t=Zn()),V.style[Ot]=Dt+t+kt}function ei(t,e,n,i){var a=t+rt;ft||(a=Math.min(a,Lt));for(var r=t;r<a;r++){var o=G[r];i||(o.style.left=100*(r-It)/rt+"%"),C&&u&&(o.style[u]=o.style[l]=C*(r-t)/1e3+"s"),Wi(o,e),zi(o,n),i&&At.push(o)}}function ni(t,e){Ht&&_e(),(It!==Pt||e)&&(Qt.emit("indexChanged",Ei()),Qt.emit("transitionStart",Ei()),dt&&Pn(),Pe&&t&&0<=["click","keydown"].indexOf(t.type)&&fi(),Vt=!0,Ze())}function ii(t){return t.toLowerCase().replace(/-/g,"")}function ai(t){if(I||Vt){if(Qt.emit("transitionEnd",Ei(t)),!I&&0<At.length)for(var e=0;e<At.length;e++){var n=At[e];n.style.left="",l&&u&&(n.style[l]="",n.style[u]=""),Wi(n,z),zi(n,W)}if(!t||!I&&t.target.parentNode===V||t.target===V&&ii(t.propertyName)===ii(Ot)){if(!Ht){var i=It;_e(),It!==i&&(Qt.emit("indexChanged",Ei()),$n())}"inner"===R&&Qt.emit("innerLoaded",Ei()),Vt=!1,Pt=It}}}function ri(t,e){if(!_t)if("prev"===t)oi(e,-1);else if("next"===t)oi(e,1);else{if(Vt){if(qt)return;ai()}var n=nn(),i=0;if("first"===t?i=-n:"last"===t?i=I?Q-rt-n:Q-1-n:("number"!=typeof t&&(t=parseInt(t)),isNaN(t)||(e||(t=Math.max(0,Math.min(Q-1,t))),i=t-n)),!I&&i&&Math.abs(i)<rt){var a=0<i?1:-1;i+=zt<=It+i-Q?Q*a:2*Q*a*-1}It+=i,I&&ft&&(It<zt&&(It+=Q),Wt<It&&(It-=Q)),nn(It)!==nn(Pt)&&ni(e)}}function oi(t,e){if(Vt){if(qt)return;ai()}var n;if(!e){for(var i=hi(t=pi(t));i!==xe&&[we,Ce].indexOf(i)<0;)i=i.parentNode;var a=[we,Ce].indexOf(i);0<=a&&(n=!0,e=0===a?-1:1)}if(ct){if(It===zt&&-1===e)return void ri("last",t);if(It===Wt&&1===e)return void ri("first",t)}e&&(It+=ot*e,$&&(It=Math.floor(It)),ni(n||t&&"keydown"===t.type?t:null))}function ui(){Ie=setInterval(function(){oi(null,Fe)},xt),Pe=!0}function li(){clearInterval(Ie),Pe=!1}function si(t,e){ji(je,{"data-action":t}),je.innerHTML=Ge[0]+t+Ge[1]+e}function ci(){ui(),je&&si("stop",bt[1])}function fi(){li(),je&&si("start",bt[0])}function di(){Pe?(fi(),We=!0):(ci(),We=!1)}function vi(t){t.focus()}function pi(t){return mi(t=t||m.event)?t.changedTouches[0]:t}function hi(t){return t.target||m.event.srcElement}function mi(t){return 0<=t.type.indexOf("touch")}function yi(t){t.preventDefault?t.preventDefault():t.returnValue=!1}function gi(){return a=Ke.y-Ye.y,r=Ke.x-Ye.x,t=Math.atan2(a,r)*(180/Math.PI),e=Ft,n=!1,i=Math.abs(90-Math.abs(t)),90-e<=i?n="horizontal":i<=e&&(n="vertical"),n===H.axis;var t,e,n,i,a,r}function xi(t){if(Vt){if(qt)return;ai()}gt&&Pe&&li(),Je=!0,Xe&&(Ni(Xe),Xe=null);var e=pi(t);Qt.emit(mi(t)?"touchStart":"dragStart",Ei(t)),!mi(t)&&0<=["img","a"].indexOf(Gn(hi(t)))&&yi(t),Ke.x=Ye.x=e.clientX,Ke.y=Ye.y=e.clientY,I&&(Qe=parseFloat(V.style[Ot].replace(Dt,"")),Jn(V,"0s"))}function bi(t){if(Je){var e=pi(t);Ke.x=e.clientX,Ke.y=e.clientY,I?Xe||(Xe=Ai(function(){!function t(e){if(!jt)return void(Je=!1);Ni(Xe);Je&&(Xe=Ai(function(){t(e)}));"?"===jt&&(jt=gi());if(jt){!me&&mi(e)&&(me=!0);try{e.type&&Qt.emit(mi(e)?"touchMove":"dragMove",Ei(e))}catch(t){}var n=Qe,i=Ue(Ke,Ye);if(!F||tt||$)n+=i,n+="px";else{var a=r?i*rt*100/((it+nt)*Lt):100*i/(it+nt);n+=a,n+="%"}V.style[Ot]=Dt+n+kt}}(t)})):("?"===jt&&(jt=gi()),jt&&(me=!0)),("boolean"!=typeof t.cancelable||t.cancelable)&&me&&t.preventDefault()}}function wi(i){if(Je){Xe&&(Ni(Xe),Xe=null),I&&Jn(V,""),Je=!1;var t=pi(i);Ke.x=t.clientX,Ke.y=t.clientY;var a=Ue(Ke,Ye);if(Math.abs(a)){if(!mi(i)){var n=hi(i);Ui(n,{click:function t(e){yi(e),_i(n,{click:t})}})}I?Xe=Ai(function(){if(F&&!$){var t=-a*rt/(it+nt);t=0<a?Math.floor(t):Math.ceil(t),It+=t}else{var e=-(Qe+a);if(e<=0)It=zt;else if(e>=N[Lt-1])It=Wt;else for(var n=0;n<Lt&&e>=N[n];)e>N[It=n]&&a<0&&(It+=1),n++}ni(i,a),Qt.emit(mi(i)?"touchEnd":"dragEnd",Ei(i))}):jt&&oi(i,0<a?-1:1)}}"auto"===H.preventScrollOnTouch&&(me=!1),Ft&&(jt="?"),gt&&!Pe&&ui()}function Ci(){(M||j).style.height=N[It+rt]-N[It]+"px"}function Mi(){var t=tt?(tt+nt)*Q/it:Q/rt;return Math.min(Math.ceil(t),Q)}function Ti(){if(ht&&!le&&Le!==Be){var t=Be,e=Le,n=Xi;for(Le<Be&&(t=Le,e=Be,n=Qi);t<e;)n(Ee[t]),t++;Be=Le}}function Ei(t){return{container:V,slideItems:G,navContainer:Ae,navItems:Ee,controlsContainer:xe,hasControls:oe,prevButton:we,nextButton:Ce,items:rt,slideBy:ot,cloneCount:Nt,slideCount:Q,slideCountNew:Lt,index:It,indexCached:Pt,displayIndex:tn(),navCurrentIndex:He,navCurrentIndexCached:Oe,pages:Le,pagesCached:Be,sheet:Mt,isOn:Y,event:t||{}}}f&&console.warn("No slides found in",H.container)};return $i}();


typeof navigator === "object" && (function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
  typeof define === 'function' && define.amd ? define('Plyr', factory) :
  (global = typeof globalThis !== 'undefined' ? globalThis : global || self, global.Plyr = factory());
})(this, (function () { 'use strict';

  function _defineProperty$1(obj, key, value) {
    key = _toPropertyKey(key);
    if (key in obj) {
      Object.defineProperty(obj, key, {
        value: value,
        enumerable: true,
        configurable: true,
        writable: true
      });
    } else {
      obj[key] = value;
    }
    return obj;
  }
  function _toPrimitive(input, hint) {
    if (typeof input !== "object" || input === null) return input;
    var prim = input[Symbol.toPrimitive];
    if (prim !== undefined) {
      var res = prim.call(input, hint || "default");
      if (typeof res !== "object") return res;
      throw new TypeError("@@toPrimitive must return a primitive value.");
    }
    return (hint === "string" ? String : Number)(input);
  }
  function _toPropertyKey(arg) {
    var key = _toPrimitive(arg, "string");
    return typeof key === "symbol" ? key : String(key);
  }

  function _classCallCheck(e, t) {
    if (!(e instanceof t)) throw new TypeError("Cannot call a class as a function");
  }
  function _defineProperties(e, t) {
    for (var n = 0; n < t.length; n++) {
      var r = t[n];
      r.enumerable = r.enumerable || !1, r.configurable = !0, "value" in r && (r.writable = !0), Object.defineProperty(e, r.key, r);
    }
  }
  function _createClass(e, t, n) {
    return t && _defineProperties(e.prototype, t), n && _defineProperties(e, n), e;
  }
  function _defineProperty(e, t, n) {
    return t in e ? Object.defineProperty(e, t, {
      value: n,
      enumerable: !0,
      configurable: !0,
      writable: !0
    }) : e[t] = n, e;
  }
  function ownKeys(e, t) {
    var n = Object.keys(e);
    if (Object.getOwnPropertySymbols) {
      var r = Object.getOwnPropertySymbols(e);
      t && (r = r.filter(function (t) {
        return Object.getOwnPropertyDescriptor(e, t).enumerable;
      })), n.push.apply(n, r);
    }
    return n;
  }
  function _objectSpread2(e) {
    for (var t = 1; t < arguments.length; t++) {
      var n = null != arguments[t] ? arguments[t] : {};
      t % 2 ? ownKeys(Object(n), !0).forEach(function (t) {
        _defineProperty(e, t, n[t]);
      }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : ownKeys(Object(n)).forEach(function (t) {
        Object.defineProperty(e, t, Object.getOwnPropertyDescriptor(n, t));
      });
    }
    return e;
  }
  var defaults$1 = {
    addCSS: !0,
    thumbWidth: 15,
    watch: !0
  };
  function matches$1(e, t) {
    return function () {
      return Array.from(document.querySelectorAll(t)).includes(this);
    }.call(e, t);
  }
  function trigger(e, t) {
    if (e && t) {
      var n = new Event(t, {
        bubbles: !0
      });
      e.dispatchEvent(n);
    }
  }
  var getConstructor$1 = function (e) {
      return null != e ? e.constructor : null;
    },
    instanceOf$1 = function (e, t) {
      return !!(e && t && e instanceof t);
    },
    isNullOrUndefined$1 = function (e) {
      return null == e;
    },
    isObject$1 = function (e) {
      return getConstructor$1(e) === Object;
    },
    isNumber$1 = function (e) {
      return getConstructor$1(e) === Number && !Number.isNaN(e);
    },
    isString$1 = function (e) {
      return getConstructor$1(e) === String;
    },
    isBoolean$1 = function (e) {
      return getConstructor$1(e) === Boolean;
    },
    isFunction$1 = function (e) {
      return getConstructor$1(e) === Function;
    },
    isArray$1 = function (e) {
      return Array.isArray(e);
    },
    isNodeList$1 = function (e) {
      return instanceOf$1(e, NodeList);
    },
    isElement$1 = function (e) {
      return instanceOf$1(e, Element);
    },
    isEvent$1 = function (e) {
      return instanceOf$1(e, Event);
    },
    isEmpty$1 = function (e) {
      return isNullOrUndefined$1(e) || (isString$1(e) || isArray$1(e) || isNodeList$1(e)) && !e.length || isObject$1(e) && !Object.keys(e).length;
    },
    is$1 = {
      nullOrUndefined: isNullOrUndefined$1,
      object: isObject$1,
      number: isNumber$1,
      string: isString$1,
      boolean: isBoolean$1,
      function: isFunction$1,
      array: isArray$1,
      nodeList: isNodeList$1,
      element: isElement$1,
      event: isEvent$1,
      empty: isEmpty$1
    };
  function getDecimalPlaces(e) {
    var t = "".concat(e).match(/(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/);
    return t ? Math.max(0, (t[1] ? t[1].length : 0) - (t[2] ? +t[2] : 0)) : 0;
  }
  function round(e, t) {
    if (1 > t) {
      var n = getDecimalPlaces(t);
      return parseFloat(e.toFixed(n));
    }
    return Math.round(e / t) * t;
  }
  var RangeTouch = function () {
    function e(t, n) {
      _classCallCheck(this, e), is$1.element(t) ? this.element = t : is$1.string(t) && (this.element = document.querySelector(t)), is$1.element(this.element) && is$1.empty(this.element.rangeTouch) && (this.config = _objectSpread2({}, defaults$1, {}, n), this.init());
    }
    return _createClass(e, [{
      key: "init",
      value: function () {
        e.enabled && (this.config.addCSS && (this.element.style.userSelect = "none", this.element.style.webKitUserSelect = "none", this.element.style.touchAction = "manipulation"), this.listeners(!0), this.element.rangeTouch = this);
      }
    }, {
      key: "destroy",
      value: function () {
        e.enabled && (this.config.addCSS && (this.element.style.userSelect = "", this.element.style.webKitUserSelect = "", this.element.style.touchAction = ""), this.listeners(!1), this.element.rangeTouch = null);
      }
    }, {
      key: "listeners",
      value: function (e) {
        var t = this,
          n = e ? "addEventListener" : "removeEventListener";
        ["touchstart", "touchmove", "touchend"].forEach(function (e) {
          t.element[n](e, function (e) {
            return t.set(e);
          }, !1);
        });
      }
    }, {
      key: "get",
      value: function (t) {
        if (!e.enabled || !is$1.event(t)) return null;
        var n,
          r = t.target,
          i = t.changedTouches[0],
          o = parseFloat(r.getAttribute("min")) || 0,
          s = parseFloat(r.getAttribute("max")) || 100,
          u = parseFloat(r.getAttribute("step")) || 1,
          c = r.getBoundingClientRect(),
          a = 100 / c.width * (this.config.thumbWidth / 2) / 100;
        return 0 > (n = 100 / c.width * (i.clientX - c.left)) ? n = 0 : 100 < n && (n = 100), 50 > n ? n -= (100 - 2 * n) * a : 50 < n && (n += 2 * (n - 50) * a), o + round(n / 100 * (s - o), u);
      }
    }, {
      key: "set",
      value: function (t) {
        e.enabled && is$1.event(t) && !t.target.disabled && (t.preventDefault(), t.target.value = this.get(t), trigger(t.target, "touchend" === t.type ? "change" : "input"));
      }
    }], [{
      key: "setup",
      value: function (t) {
        var n = 1 < arguments.length && void 0 !== arguments[1] ? arguments[1] : {},
          r = null;
        if (is$1.empty(t) || is$1.string(t) ? r = Array.from(document.querySelectorAll(is$1.string(t) ? t : 'input[type="range"]')) : is$1.element(t) ? r = [t] : is$1.nodeList(t) ? r = Array.from(t) : is$1.array(t) && (r = t.filter(is$1.element)), is$1.empty(r)) return null;
        var i = _objectSpread2({}, defaults$1, {}, n);
        if (is$1.string(t) && i.watch) {
          var o = new MutationObserver(function (n) {
            Array.from(n).forEach(function (n) {
              Array.from(n.addedNodes).forEach(function (n) {
                is$1.element(n) && matches$1(n, t) && new e(n, i);
              });
            });
          });
          o.observe(document.body, {
            childList: !0,
            subtree: !0
          });
        }
        return r.map(function (t) {
          return new e(t, n);
        });
      }
    }, {
      key: "enabled",
      get: function () {
        return "ontouchstart" in document.documentElement;
      }
    }]), e;
  }();

  // ==========================================================================
  // Type checking utils
  // ==========================================================================

  const getConstructor = input => input !== null && typeof input !== 'undefined' ? input.constructor : null;
  const instanceOf = (input, constructor) => Boolean(input && constructor && input instanceof constructor);
  const isNullOrUndefined = input => input === null || typeof input === 'undefined';
  const isObject = input => getConstructor(input) === Object;
  const isNumber = input => getConstructor(input) === Number && !Number.isNaN(input);
  const isString = input => getConstructor(input) === String;
  const isBoolean = input => getConstructor(input) === Boolean;
  const isFunction = input => typeof input === 'function';
  const isArray = input => Array.isArray(input);
  const isWeakMap = input => instanceOf(input, WeakMap);
  const isNodeList = input => instanceOf(input, NodeList);
  const isTextNode = input => getConstructor(input) === Text;
  const isEvent = input => instanceOf(input, Event);
  const isKeyboardEvent = input => instanceOf(input, KeyboardEvent);
  const isCue = input => instanceOf(input, window.TextTrackCue) || instanceOf(input, window.VTTCue);
  const isTrack = input => instanceOf(input, TextTrack) || !isNullOrUndefined(input) && isString(input.kind);
  const isPromise = input => instanceOf(input, Promise) && isFunction(input.then);
  const isElement = input => input !== null && typeof input === 'object' && input.nodeType === 1 && typeof input.style === 'object' && typeof input.ownerDocument === 'object';
  const isEmpty = input => isNullOrUndefined(input) || (isString(input) || isArray(input) || isNodeList(input)) && !input.length || isObject(input) && !Object.keys(input).length;
  const isUrl = input => {
    // Accept a URL object
    if (instanceOf(input, window.URL)) {
      return true;
    }

    // Must be string from here
    if (!isString(input)) {
      return false;
    }

    // Add the protocol if required
    let string = input;
    if (!input.startsWith('http://') || !input.startsWith('https://')) {
      string = `http://${input}`;
    }
    try {
      return !isEmpty(new URL(string).hostname);
    } catch (_) {
      return false;
    }
  };
  var is = {
    nullOrUndefined: isNullOrUndefined,
    object: isObject,
    number: isNumber,
    string: isString,
    boolean: isBoolean,
    function: isFunction,
    array: isArray,
    weakMap: isWeakMap,
    nodeList: isNodeList,
    element: isElement,
    textNode: isTextNode,
    event: isEvent,
    keyboardEvent: isKeyboardEvent,
    cue: isCue,
    track: isTrack,
    promise: isPromise,
    url: isUrl,
    empty: isEmpty
  };

  // ==========================================================================
  const transitionEndEvent = (() => {
    const element = document.createElement('span');
    const events = {
      WebkitTransition: 'webkitTransitionEnd',
      MozTransition: 'transitionend',
      OTransition: 'oTransitionEnd otransitionend',
      transition: 'transitionend'
    };
    const type = Object.keys(events).find(event => element.style[event] !== undefined);
    return is.string(type) ? events[type] : false;
  })();

  // Force repaint of element
  function repaint(element, delay) {
    setTimeout(() => {
      try {
        // eslint-disable-next-line no-param-reassign
        element.hidden = true;

        // eslint-disable-next-line no-unused-expressions
        element.offsetHeight;

        // eslint-disable-next-line no-param-reassign
        element.hidden = false;
      } catch (_) {
        // Do nothing
      }
    }, delay);
  }

  // ==========================================================================
  // Browser sniffing
  // Unfortunately, due to mixed support, UA sniffing is required
  // ==========================================================================

  const isIE = Boolean(window.document.documentMode);
  const isEdge = /Edge/g.test(navigator.userAgent);
  const isWebKit = 'WebkitAppearance' in document.documentElement.style && !/Edge/g.test(navigator.userAgent);
  const isIPhone = /iPhone|iPod/gi.test(navigator.userAgent) && navigator.maxTouchPoints > 1;
  // navigator.platform may be deprecated but this check is still required
  const isIPadOS = navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1;
  const isIos = /iPad|iPhone|iPod/gi.test(navigator.userAgent) && navigator.maxTouchPoints > 1;
  var browser = {
    isIE,
    isEdge,
    isWebKit,
    isIPhone,
    isIPadOS,
    isIos
  };

  // ==========================================================================

  // Clone nested objects
  function cloneDeep(object) {
    return JSON.parse(JSON.stringify(object));
  }

  // Get a nested value in an object
  function getDeep(object, path) {
    return path.split('.').reduce((obj, key) => obj && obj[key], object);
  }

  // Deep extend destination object with N more objects
  function extend(target = {}, ...sources) {
    if (!sources.length) {
      return target;
    }
    const source = sources.shift();
    if (!is.object(source)) {
      return target;
    }
    Object.keys(source).forEach(key => {
      if (is.object(source[key])) {
        if (!Object.keys(target).includes(key)) {
          Object.assign(target, {
            [key]: {}
          });
        }
        extend(target[key], source[key]);
      } else {
        Object.assign(target, {
          [key]: source[key]
        });
      }
    });
    return extend(target, ...sources);
  }

  // ==========================================================================

  // Wrap an element
  function wrap(elements, wrapper) {
    // Convert `elements` to an array, if necessary.
    const targets = elements.length ? elements : [elements];

    // Loops backwards to prevent having to clone the wrapper on the
    // first element (see `child` below).
    Array.from(targets).reverse().forEach((element, index) => {
      const child = index > 0 ? wrapper.cloneNode(true) : wrapper;
      // Cache the current parent and sibling.
      const parent = element.parentNode;
      const sibling = element.nextSibling;

      // Wrap the element (is automatically removed from its current
      // parent).
      child.appendChild(element);

      // If the element had a sibling, insert the wrapper before
      // the sibling to maintain the HTML structure; otherwise, just
      // append it to the parent.
      if (sibling) {
        parent.insertBefore(child, sibling);
      } else {
        parent.appendChild(child);
      }
    });
  }

  // Set attributes
  function setAttributes(element, attributes) {
    if (!is.element(element) || is.empty(attributes)) return;

    // Assume null and undefined attributes should be left out,
    // Setting them would otherwise convert them to "null" and "undefined"
    Object.entries(attributes).filter(([, value]) => !is.nullOrUndefined(value)).forEach(([key, value]) => element.setAttribute(key, value));
  }

  // Create a DocumentFragment
  function createElement(type, attributes, text) {
    // Create a new <element>
    const element = document.createElement(type);

    // Set all passed attributes
    if (is.object(attributes)) {
      setAttributes(element, attributes);
    }

    // Add text node
    if (is.string(text)) {
      element.innerText = text;
    }

    // Return built element
    return element;
  }

  // Insert an element after another
  function insertAfter(element, target) {
    if (!is.element(element) || !is.element(target)) return;
    target.parentNode.insertBefore(element, target.nextSibling);
  }

  // Insert a DocumentFragment
  function insertElement(type, parent, attributes, text) {
    if (!is.element(parent)) return;
    parent.appendChild(createElement(type, attributes, text));
  }

  // Remove element(s)
  function removeElement(element) {
    if (is.nodeList(element) || is.array(element)) {
      Array.from(element).forEach(removeElement);
      return;
    }
    if (!is.element(element) || !is.element(element.parentNode)) {
      return;
    }
    element.parentNode.removeChild(element);
  }

  // Remove all child elements
  function emptyElement(element) {
    if (!is.element(element)) return;
    let {
      length
    } = element.childNodes;
    while (length > 0) {
      element.removeChild(element.lastChild);
      length -= 1;
    }
  }

  // Replace element
  function replaceElement(newChild, oldChild) {
    if (!is.element(oldChild) || !is.element(oldChild.parentNode) || !is.element(newChild)) return null;
    oldChild.parentNode.replaceChild(newChild, oldChild);
    return newChild;
  }

  // Get an attribute object from a string selector
  function getAttributesFromSelector(sel, existingAttributes) {
    // For example:
    // '.test' to { class: 'test' }
    // '#test' to { id: 'test' }
    // '[data-test="test"]' to { 'data-test': 'test' }

    if (!is.string(sel) || is.empty(sel)) return {};
    const attributes = {};
    const existing = extend({}, existingAttributes);
    sel.split(',').forEach(s => {
      // Remove whitespace
      const selector = s.trim();
      const className = selector.replace('.', '');
      const stripped = selector.replace(/[[\]]/g, '');
      // Get the parts and value
      const parts = stripped.split('=');
      const [key] = parts;
      const value = parts.length > 1 ? parts[1].replace(/["']/g, '') : '';
      // Get the first character
      const start = selector.charAt(0);
      switch (start) {
        case '.':
          // Add to existing classname
          if (is.string(existing.class)) {
            attributes.class = `${existing.class} ${className}`;
          } else {
            attributes.class = className;
          }
          break;
        case '#':
          // ID selector
          attributes.id = selector.replace('#', '');
          break;
        case '[':
          // Attribute selector
          attributes[key] = value;
          break;
      }
    });
    return extend(existing, attributes);
  }

  // Toggle hidden
  function toggleHidden(element, hidden) {
    if (!is.element(element)) return;
    let hide = hidden;
    if (!is.boolean(hide)) {
      hide = !element.hidden;
    }

    // eslint-disable-next-line no-param-reassign
    element.hidden = hide;
  }

  // Mirror Element.classList.toggle, with IE compatibility for "force" argument
  function toggleClass(element, className, force) {
    if (is.nodeList(element)) {
      return Array.from(element).map(e => toggleClass(e, className, force));
    }
    if (is.element(element)) {
      let method = 'toggle';
      if (typeof force !== 'undefined') {
        method = force ? 'add' : 'remove';
      }
      element.classList[method](className);
      return element.classList.contains(className);
    }
    return false;
  }

  // Has class name
  function hasClass(element, className) {
    return is.element(element) && element.classList.contains(className);
  }

  // Element matches selector
  function matches(element, selector) {
    const {
      prototype
    } = Element;
    function match() {
      return Array.from(document.querySelectorAll(selector)).includes(this);
    }
    const method = prototype.matches || prototype.webkitMatchesSelector || prototype.mozMatchesSelector || prototype.msMatchesSelector || match;
    return method.call(element, selector);
  }

  // Closest ancestor element matching selector (also tests element itself)
  function closest$1(element, selector) {
    const {
      prototype
    } = Element;

    // https://developer.mozilla.org/en-US/docs/Web/API/Element/closest#Polyfill
    function closestElement() {
      let el = this;
      do {
        if (matches.matches(el, selector)) return el;
        el = el.parentElement || el.parentNode;
      } while (el !== null && el.nodeType === 1);
      return null;
    }
    const method = prototype.closest || closestElement;
    return method.call(element, selector);
  }

  // Find all elements
  function getElements(selector) {
    return this.elements.container.querySelectorAll(selector);
  }

  // Find a single element
  function getElement(selector) {
    return this.elements.container.querySelector(selector);
  }

  // Set focus and tab focus class
  function setFocus(element = null, focusVisible = false) {
    if (!is.element(element)) return;

    // Set regular focus
    element.focus({
      preventScroll: true,
      focusVisible
    });
  }

  // ==========================================================================

  // Default codecs for checking mimetype support
  const defaultCodecs = {
    'audio/ogg': 'vorbis',
    'audio/wav': '1',
    'video/webm': 'vp8, vorbis',
    'video/mp4': 'avc1.42E01E, mp4a.40.2',
    'video/ogg': 'theora'
  };

  // Check for feature support
  const support = {
    // Basic support
    audio: 'canPlayType' in document.createElement('audio'),
    video: 'canPlayType' in document.createElement('video'),
    // Check for support
    // Basic functionality vs full UI
    check(type, provider) {
      const api = support[type] || provider !== 'html5';
      const ui = api && support.rangeInput;
      return {
        api,
        ui
      };
    },
    // Picture-in-picture support
    // Safari & Chrome only currently
    pip: (() => {
      // While iPhone's support picture-in-picture for some apps, seemingly Safari isn't one of them
      // It will throw the following error when trying to enter picture-in-picture
      // `NotSupportedError: The Picture-in-Picture mode is not supported.`
      if (browser.isIPhone) {
        return false;
      }

      // Safari
      // https://developer.apple.com/documentation/webkitjs/adding_picture_in_picture_to_your_safari_media_controls
      if (is.function(createElement('video').webkitSetPresentationMode)) {
        return true;
      }

      // Chrome
      // https://developers.google.com/web/updates/2018/10/watch-video-using-picture-in-picture
      if (document.pictureInPictureEnabled && !createElement('video').disablePictureInPicture) {
        return true;
      }
      return false;
    })(),
    // Airplay support
    // Safari only currently
    airplay: is.function(window.WebKitPlaybackTargetAvailabilityEvent),
    // Inline playback support
    // https://webkit.org/blog/6784/new-video-policies-for-ios/
    playsinline: 'playsInline' in document.createElement('video'),
    // Check for mime type support against a player instance
    // Credits: http://diveintohtml5.info/everything.html
    // Related: http://www.leanbackplayer.com/test/h5mt.html
    mime(input) {
      if (is.empty(input)) {
        return false;
      }
      const [mediaType] = input.split('/');
      let type = input;

      // Verify we're using HTML5 and there's no media type mismatch
      if (!this.isHTML5 || mediaType !== this.type) {
        return false;
      }

      // Add codec if required
      if (Object.keys(defaultCodecs).includes(type)) {
        type += `; codecs="${defaultCodecs[input]}"`;
      }
      try {
        return Boolean(type && this.media.canPlayType(type).replace(/no/, ''));
      } catch (_) {
        return false;
      }
    },
    // Check for textTracks support
    textTracks: 'textTracks' in document.createElement('video'),
    // <input type="range"> Sliders
    rangeInput: (() => {
      const range = document.createElement('input');
      range.type = 'range';
      return range.type === 'range';
    })(),
    // Touch
    // NOTE: Remember a device can be mouse + touch enabled so we check on first touch event
    touch: 'ontouchstart' in document.documentElement,
    // Detect transitions support
    transitions: transitionEndEvent !== false,
    // Reduced motion iOS & MacOS setting
    // https://webkit.org/blog/7551/responsive-design-for-motion/
    reducedMotion: 'matchMedia' in window && window.matchMedia('(prefers-reduced-motion)').matches
  };

  // ==========================================================================

  // Check for passive event listener support
  // https://github.com/WICG/EventListenerOptions/blob/gh-pages/explainer.md
  // https://www.youtube.com/watch?v=NPM6172J22g
  const supportsPassiveListeners = (() => {
    // Test via a getter in the options object to see if the passive property is accessed
    let supported = false;
    try {
      const options = Object.defineProperty({}, 'passive', {
        get() {
          supported = true;
          return null;
        }
      });
      window.addEventListener('test', null, options);
      window.removeEventListener('test', null, options);
    } catch (_) {
      // Do nothing
    }
    return supported;
  })();

  // Toggle event listener
  function toggleListener(element, event, callback, toggle = false, passive = true, capture = false) {
    // Bail if no element, event, or callback
    if (!element || !('addEventListener' in element) || is.empty(event) || !is.function(callback)) {
      return;
    }

    // Allow multiple events
    const events = event.split(' ');
    // Build options
    // Default to just the capture boolean for browsers with no passive listener support
    let options = capture;

    // If passive events listeners are supported
    if (supportsPassiveListeners) {
      options = {
        // Whether the listener can be passive (i.e. default never prevented)
        passive,
        // Whether the listener is a capturing listener or not
        capture
      };
    }

    // If a single node is passed, bind the event listener
    events.forEach(type => {
      if (this && this.eventListeners && toggle) {
        // Cache event listener
        this.eventListeners.push({
          element,
          type,
          callback,
          options
        });
      }
      element[toggle ? 'addEventListener' : 'removeEventListener'](type, callback, options);
    });
  }

  // Bind event handler
  function on(element, events = '', callback, passive = true, capture = false) {
    toggleListener.call(this, element, events, callback, true, passive, capture);
  }

  // Unbind event handler
  function off(element, events = '', callback, passive = true, capture = false) {
    toggleListener.call(this, element, events, callback, false, passive, capture);
  }

  // Bind once-only event handler
  function once(element, events = '', callback, passive = true, capture = false) {
    const onceCallback = (...args) => {
      off(element, events, onceCallback, passive, capture);
      callback.apply(this, args);
    };
    toggleListener.call(this, element, events, onceCallback, true, passive, capture);
  }

  // Trigger event
  function triggerEvent(element, type = '', bubbles = false, detail = {}) {
    // Bail if no element
    if (!is.element(element) || is.empty(type)) {
      return;
    }

    // Create and dispatch the event
    const event = new CustomEvent(type, {
      bubbles,
      detail: {
        ...detail,
        plyr: this
      }
    });

    // Dispatch the event
    element.dispatchEvent(event);
  }

  // Unbind all cached event listeners
  function unbindListeners() {
    if (this && this.eventListeners) {
      this.eventListeners.forEach(item => {
        const {
          element,
          type,
          callback,
          options
        } = item;
        element.removeEventListener(type, callback, options);
      });
      this.eventListeners = [];
    }
  }

  // Run method when / if player is ready
  function ready() {
    return new Promise(resolve => this.ready ? setTimeout(resolve, 0) : on.call(this, this.elements.container, 'ready', resolve)).then(() => {});
  }

  /**
   * Silence a Promise-like object.
   * This is useful for avoiding non-harmful, but potentially confusing "uncaught
   * play promise" rejection error messages.
   * @param  {Object} value An object that may or may not be `Promise`-like.
   */
  function silencePromise(value) {
    if (is.promise(value)) {
      value.then(null, () => {});
    }
  }

  // ==========================================================================

  // Remove duplicates in an array
  function dedupe(array) {
    if (!is.array(array)) {
      return array;
    }
    return array.filter((item, index) => array.indexOf(item) === index);
  }

  // Get the closest value in an array
  function closest(array, value) {
    if (!is.array(array) || !array.length) {
      return null;
    }
    return array.reduce((prev, curr) => Math.abs(curr - value) < Math.abs(prev - value) ? curr : prev);
  }

  // ==========================================================================

  // Check support for a CSS declaration
  function supportsCSS(declaration) {
    if (!window || !window.CSS) {
      return false;
    }
    return window.CSS.supports(declaration);
  }

  // Standard/common aspect ratios
  const standardRatios = [[1, 1], [4, 3], [3, 4], [5, 4], [4, 5], [3, 2], [2, 3], [16, 10], [10, 16], [16, 9], [9, 16], [21, 9], [9, 21], [32, 9], [9, 32]].reduce((out, [x, y]) => ({
    ...out,
    [x / y]: [x, y]
  }), {});

  // Validate an aspect ratio
  function validateAspectRatio(input) {
    if (!is.array(input) && (!is.string(input) || !input.includes(':'))) {
      return false;
    }
    const ratio = is.array(input) ? input : input.split(':');
    return ratio.map(Number).every(is.number);
  }

  // Reduce an aspect ratio to it's lowest form
  function reduceAspectRatio(ratio) {
    if (!is.array(ratio) || !ratio.every(is.number)) {
      return null;
    }
    const [width, height] = ratio;
    const getDivider = (w, h) => h === 0 ? w : getDivider(h, w % h);
    const divider = getDivider(width, height);
    return [width / divider, height / divider];
  }

  // Calculate an aspect ratio
  function getAspectRatio(input) {
    const parse = ratio => validateAspectRatio(ratio) ? ratio.split(':').map(Number) : null;
    // Try provided ratio
    let ratio = parse(input);

    // Get from config
    if (ratio === null) {
      ratio = parse(this.config.ratio);
    }

    // Get from embed
    if (ratio === null && !is.empty(this.embed) && is.array(this.embed.ratio)) {
      ({
        ratio
      } = this.embed);
    }

    // Get from HTML5 video
    if (ratio === null && this.isHTML5) {
      const {
        videoWidth,
        videoHeight
      } = this.media;
      ratio = [videoWidth, videoHeight];
    }
    return reduceAspectRatio(ratio);
  }

  // Set aspect ratio for responsive container
  function setAspectRatio(input) {
    if (!this.isVideo) {
      return {};
    }
    const {
      wrapper
    } = this.elements;
    const ratio = getAspectRatio.call(this, input);
    if (!is.array(ratio)) {
      return {};
    }
    const [x, y] = reduceAspectRatio(ratio);
    const useNative = supportsCSS(`aspect-ratio: ${x}/${y}`);
    const padding = 100 / x * y;
    if (useNative) {
      wrapper.style.aspectRatio = `${x}/${y}`;
    } else {
      wrapper.style.paddingBottom = `${padding}%`;
    }

    // For Vimeo we have an extra <div> to hide the standard controls and UI
    if (this.isVimeo && !this.config.vimeo.premium && this.supported.ui) {
      const height = 100 / this.media.offsetWidth * parseInt(window.getComputedStyle(this.media).paddingBottom, 10);
      const offset = (height - padding) / (height / 50);
      if (this.fullscreen.active) {
        wrapper.style.paddingBottom = null;
      } else {
        this.media.style.transform = `translateY(-${offset}%)`;
      }
    } else if (this.isHTML5) {
      wrapper.classList.add(this.config.classNames.videoFixedRatio);
    }
    return {
      padding,
      ratio
    };
  }

  // Round an aspect ratio to closest standard ratio
  function roundAspectRatio(x, y, tolerance = 0.05) {
    const ratio = x / y;
    const closestRatio = closest(Object.keys(standardRatios), ratio);

    // Check match is within tolerance
    if (Math.abs(closestRatio - ratio) <= tolerance) {
      return standardRatios[closestRatio];
    }

    // No match
    return [x, y];
  }

  // Get the size of the viewport
  // https://stackoverflow.com/questions/1248081/how-to-get-the-browser-viewport-dimensions
  function getViewportSize() {
    const width = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    const height = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
    return [width, height];
  }

  // ==========================================================================
  const html5 = {
    getSources() {
      if (!this.isHTML5) {
        return [];
      }
      const sources = Array.from(this.media.querySelectorAll('source'));

      // Filter out unsupported sources (if type is specified)
      return sources.filter(source => {
        const type = source.getAttribute('type');
        if (is.empty(type)) {
          return true;
        }
        return support.mime.call(this, type);
      });
    },
    // Get quality levels
    getQualityOptions() {
      // Whether we're forcing all options (e.g. for streaming)
      if (this.config.quality.forced) {
        return this.config.quality.options;
      }

      // Get sizes from <source> elements
      return html5.getSources.call(this).map(source => Number(source.getAttribute('size'))).filter(Boolean);
    },
    setup() {
      if (!this.isHTML5) {
        return;
      }
      const player = this;

      // Set speed options from config
      player.options.speed = player.config.speed.options;

      // Set aspect ratio if fixed
      if (!is.empty(this.config.ratio)) {
        setAspectRatio.call(player);
      }

      // Quality
      Object.defineProperty(player.media, 'quality', {
        get() {
          // Get sources
          const sources = html5.getSources.call(player);
          const source = sources.find(s => s.getAttribute('src') === player.source);

          // Return size, if match is found
          return source && Number(source.getAttribute('size'));
        },
        set(input) {
          if (player.quality === input) {
            return;
          }

          // If we're using an external handler...
          if (player.config.quality.forced && is.function(player.config.quality.onChange)) {
            player.config.quality.onChange(input);
          } else {
            // Get sources
            const sources = html5.getSources.call(player);
            // Get first match for requested size
            const source = sources.find(s => Number(s.getAttribute('size')) === input);

            // No matching source found
            if (!source) {
              return;
            }

            // Get current state
            const {
              currentTime,
              paused,
              preload,
              readyState,
              playbackRate
            } = player.media;

            // Set new source
            player.media.src = source.getAttribute('src');

            // Prevent loading if preload="none" and the current source isn't loaded (#1044)
            if (preload !== 'none' || readyState) {
              // Restore time
              player.once('loadedmetadata', () => {
                player.speed = playbackRate;
                player.currentTime = currentTime;

                // Resume playing
                if (!paused) {
                  silencePromise(player.play());
                }
              });

              // Load new source
              player.media.load();
            }
          }

          // Trigger change event
          triggerEvent.call(player, player.media, 'qualitychange', false, {
            quality: input
          });
        }
      });
    },
    // Cancel current network requests
    // See https://github.com/sampotts/plyr/issues/174
    cancelRequests() {
      if (!this.isHTML5) {
        return;
      }

      // Remove child sources
      removeElement(html5.getSources.call(this));

      // Set blank video src attribute
      // This is to prevent a MEDIA_ERR_SRC_NOT_SUPPORTED error
      // Info: http://stackoverflow.com/questions/32231579/how-to-properly-dispose-of-an-html5-video-and-close-socket-or-connection
      this.media.setAttribute('src', this.config.blankVideo);

      // Load the new empty source
      // This will cancel existing requests
      // See https://github.com/sampotts/plyr/issues/174
      this.media.load();

      // Debugging
      this.debug.log('Cancelled network requests');
    }
  };

  // ==========================================================================

  // Generate a random ID
  function generateId(prefix) {
    return `${prefix}-${Math.floor(Math.random() * 10000)}`;
  }

  // Format string
  function format(input, ...args) {
    if (is.empty(input)) return input;
    return input.toString().replace(/{(\d+)}/g, (_, i) => args[i].toString());
  }

  // Get percentage
  function getPercentage(current, max) {
    if (current === 0 || max === 0 || Number.isNaN(current) || Number.isNaN(max)) {
      return 0;
    }
    return (current / max * 100).toFixed(2);
  }

  // Replace all occurrences of a string in a string
  const replaceAll = (input = '', find = '', replace = '') => input.replace(new RegExp(find.toString().replace(/([.*+?^=!:${}()|[\]/\\])/g, '\\$1'), 'g'), replace.toString());

  // Convert to title case
  const toTitleCase = (input = '') => input.toString().replace(/\w\S*/g, text => text.charAt(0).toUpperCase() + text.slice(1).toLowerCase());

  // Convert string to pascalCase
  function toPascalCase(input = '') {
    let string = input.toString();

    // Convert kebab case
    string = replaceAll(string, '-', ' ');

    // Convert snake case
    string = replaceAll(string, '_', ' ');

    // Convert to title case
    string = toTitleCase(string);

    // Convert to pascal case
    return replaceAll(string, ' ', '');
  }

  // Convert string to pascalCase
  function toCamelCase(input = '') {
    let string = input.toString();

    // Convert to pascal case
    string = toPascalCase(string);

    // Convert first character to lowercase
    return string.charAt(0).toLowerCase() + string.slice(1);
  }

  // Remove HTML from a string
  function stripHTML(source) {
    const fragment = document.createDocumentFragment();
    const element = document.createElement('div');
    fragment.appendChild(element);
    element.innerHTML = source;
    return fragment.firstChild.innerText;
  }

  // Like outerHTML, but also works for DocumentFragment
  function getHTML(element) {
    const wrapper = document.createElement('div');
    wrapper.appendChild(element);
    return wrapper.innerHTML;
  }

  // ==========================================================================

  // Skip i18n for abbreviations and brand names
  const resources = {
    pip: 'PIP',
    airplay: 'AirPlay',
    html5: 'HTML5',
    vimeo: 'Vimeo',
    youtube: 'YouTube'
  };
  const i18n = {
    get(key = '', config = {}) {
      if (is.empty(key) || is.empty(config)) {
        return '';
      }
      let string = getDeep(config.i18n, key);
      if (is.empty(string)) {
        if (Object.keys(resources).includes(key)) {
          return resources[key];
        }
        return '';
      }
      const replace = {
        '{seektime}': config.seekTime,
        '{title}': config.title
      };
      Object.entries(replace).forEach(([k, v]) => {
        string = replaceAll(string, k, v);
      });
      return string;
    }
  };

  class Storage {
    constructor(player) {
      _defineProperty$1(this, "get", key => {
        if (!Storage.supported || !this.enabled) {
          return null;
        }
        const store = window.localStorage.getItem(this.key);
        if (is.empty(store)) {
          return null;
        }
        const json = JSON.parse(store);
        return is.string(key) && key.length ? json[key] : json;
      });
      _defineProperty$1(this, "set", object => {
        // Bail if we don't have localStorage support or it's disabled
        if (!Storage.supported || !this.enabled) {
          return;
        }

        // Can only store objectst
        if (!is.object(object)) {
          return;
        }

        // Get current storage
        let storage = this.get();

        // Default to empty object
        if (is.empty(storage)) {
          storage = {};
        }

        // Update the working copy of the values
        extend(storage, object);

        // Update storage
        try {
          window.localStorage.setItem(this.key, JSON.stringify(storage));
        } catch (_) {
          // Do nothing
        }
      });
      this.enabled = player.config.storage.enabled;
      this.key = player.config.storage.key;
    }

    // Check for actual support (see if we can use it)
    static get supported() {
      try {
        if (!('localStorage' in window)) {
          return false;
        }
        const test = '___test';

        // Try to use it (it might be disabled, e.g. user is in private mode)
        // see: https://github.com/sampotts/plyr/issues/131
        window.localStorage.setItem(test, test);
        window.localStorage.removeItem(test);
        return true;
      } catch (_) {
        return false;
      }
    }
  }

  // ==========================================================================
  // Fetch wrapper
  // Using XHR to avoid issues with older browsers
  // ==========================================================================

  function fetch(url, responseType = 'text') {
    return new Promise((resolve, reject) => {
      try {
        const request = new XMLHttpRequest();

        // Check for CORS support
        if (!('withCredentials' in request)) {
          return;
        }
        request.addEventListener('load', () => {
          if (responseType === 'text') {
            try {
              resolve(JSON.parse(request.responseText));
            } catch (_) {
              resolve(request.responseText);
            }
          } else {
            resolve(request.response);
          }
        });
        request.addEventListener('error', () => {
          throw new Error(request.status);
        });
        request.open('GET', url, true);

        // Set the required response type
        request.responseType = responseType;
        request.send();
      } catch (error) {
        reject(error);
      }
    });
  }

  // ==========================================================================

  // Load an external SVG sprite
  function loadSprite(url, id) {
    if (!is.string(url)) {
      return;
    }
    const prefix = 'cache';
    const hasId = is.string(id);
    let isCached = false;
    const exists = () => document.getElementById(id) !== null;
    const update = (container, data) => {
      // eslint-disable-next-line no-param-reassign
      container.innerHTML = data;

      // Check again incase of race condition
      if (hasId && exists()) {
        return;
      }

      // Inject the SVG to the body
      document.body.insertAdjacentElement('afterbegin', container);
    };

    // Only load once if ID set
    if (!hasId || !exists()) {
      const useStorage = Storage.supported;
      // Create container
      const container = document.createElement('div');
      container.setAttribute('hidden', '');
      if (hasId) {
        container.setAttribute('id', id);
      }

      // Check in cache
      if (useStorage) {
        const cached = window.localStorage.getItem(`${prefix}-${id}`);
        isCached = cached !== null;
        if (isCached) {
          const data = JSON.parse(cached);
          update(container, data.content);
        }
      }

      // Get the sprite
      fetch(url).then(result => {
        if (is.empty(result)) {
          return;
        }
        if (useStorage) {
          try {
            window.localStorage.setItem(`${prefix}-${id}`, JSON.stringify({
              content: result
            }));
          } catch (_) {
            // Do nothing
          }
        }
        update(container, result);
      }).catch(() => {});
    }
  }

  // ==========================================================================

  // Time helpers
  const getHours = value => Math.trunc(value / 60 / 60 % 60, 10);
  const getMinutes = value => Math.trunc(value / 60 % 60, 10);
  const getSeconds = value => Math.trunc(value % 60, 10);

  // Format time to UI friendly string
  function formatTime(time = 0, displayHours = false, inverted = false) {
    // Bail if the value isn't a number
    if (!is.number(time)) {
      return formatTime(undefined, displayHours, inverted);
    }

    // Format time component to add leading zero
    const format = value => `0${value}`.slice(-2);
    // Breakdown to hours, mins, secs
    let hours = getHours(time);
    const mins = getMinutes(time);
    const secs = getSeconds(time);

    // Do we need to display hours?
    if (displayHours || hours > 0) {
      hours = `${hours}:`;
    } else {
      hours = '';
    }

    // Render
    return `${inverted && time > 0 ? '-' : ''}${hours}${format(mins)}:${format(secs)}`;
  }

  // ==========================================================================

  // TODO: Don't export a massive object - break down and create class
  const controls = {
    // Get icon URL
    getIconUrl() {
      const url = new URL(this.config.iconUrl, window.location);
      const host = window.location.host ? window.location.host : window.top.location.host;
      const cors = url.host !== host || browser.isIE && !window.svg4everybody;
      return {
        url: this.config.iconUrl,
        cors
      };
    },
    // Find the UI controls
    findElements() {
      try {
        this.elements.controls = getElement.call(this, this.config.selectors.controls.wrapper);

        // Buttons
        this.elements.buttons = {
          play: getElements.call(this, this.config.selectors.buttons.play),
          pause: getElement.call(this, this.config.selectors.buttons.pause),
          restart: getElement.call(this, this.config.selectors.buttons.restart),
          rewind: getElement.call(this, this.config.selectors.buttons.rewind),
          fastForward: getElement.call(this, this.config.selectors.buttons.fastForward),
          mute: getElement.call(this, this.config.selectors.buttons.mute),
          pip: getElement.call(this, this.config.selectors.buttons.pip),
          airplay: getElement.call(this, this.config.selectors.buttons.airplay),
          settings: getElement.call(this, this.config.selectors.buttons.settings),
          captions: getElement.call(this, this.config.selectors.buttons.captions),
          fullscreen: getElement.call(this, this.config.selectors.buttons.fullscreen)
        };

        // Progress
        this.elements.progress = getElement.call(this, this.config.selectors.progress);

        // Inputs
        this.elements.inputs = {
          seek: getElement.call(this, this.config.selectors.inputs.seek),
          volume: getElement.call(this, this.config.selectors.inputs.volume)
        };

        // Display
        this.elements.display = {
          buffer: getElement.call(this, this.config.selectors.display.buffer),
          currentTime: getElement.call(this, this.config.selectors.display.currentTime),
          duration: getElement.call(this, this.config.selectors.display.duration)
        };

        // Seek tooltip
        if (is.element(this.elements.progress)) {
          this.elements.display.seekTooltip = this.elements.progress.querySelector(`.${this.config.classNames.tooltip}`);
        }
        return true;
      } catch (error) {
        // Log it
        this.debug.warn('It looks like there is a problem with your custom controls HTML', error);

        // Restore native video controls
        this.toggleNativeControls(true);
        return false;
      }
    },
    // Create <svg> icon
    createIcon(type, attributes) {
      const namespace = 'http://www.w3.org/2000/svg';
      const iconUrl = controls.getIconUrl.call(this);
      const iconPath = `${!iconUrl.cors ? iconUrl.url : ''}#${this.config.iconPrefix}`;
      // Create <svg>
      const icon = document.createElementNS(namespace, 'svg');
      setAttributes(icon, extend(attributes, {
        'aria-hidden': 'true',
        focusable: 'false'
      }));

      // Create the <use> to reference sprite
      const use = document.createElementNS(namespace, 'use');
      const path = `${iconPath}-${type}`;

      // Set `href` attributes
      // https://github.com/sampotts/plyr/issues/460
      // https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/xlink:href
      if ('href' in use) {
        use.setAttributeNS('http://www.w3.org/1999/xlink', 'href', path);
      }

      // Always set the older attribute even though it's "deprecated" (it'll be around for ages)
      use.setAttributeNS('http://www.w3.org/1999/xlink', 'xlink:href', path);

      // Add <use> to <svg>
      icon.appendChild(use);
      return icon;
    },
    // Create hidden text label
    createLabel(key, attr = {}) {
      const text = i18n.get(key, this.config);
      const attributes = {
        ...attr,
        class: [attr.class, this.config.classNames.hidden].filter(Boolean).join(' ')
      };
      return createElement('span', attributes, text);
    },
    // Create a badge
    createBadge(text) {
      if (is.empty(text)) {
        return null;
      }
      const badge = createElement('span', {
        class: this.config.classNames.menu.value
      });
      badge.appendChild(createElement('span', {
        class: this.config.classNames.menu.badge
      }, text));
      return badge;
    },
    // Create a <button>
    createButton(buttonType, attr) {
      const attributes = extend({}, attr);
      let type = toCamelCase(buttonType);
      const props = {
        element: 'button',
        toggle: false,
        label: null,
        icon: null,
        labelPressed: null,
        iconPressed: null
      };
      ['element', 'icon', 'label'].forEach(key => {
        if (Object.keys(attributes).includes(key)) {
          props[key] = attributes[key];
          delete attributes[key];
        }
      });

      // Default to 'button' type to prevent form submission
      if (props.element === 'button' && !Object.keys(attributes).includes('type')) {
        attributes.type = 'button';
      }

      // Set class name
      if (Object.keys(attributes).includes('class')) {
        if (!attributes.class.split(' ').some(c => c === this.config.classNames.control)) {
          extend(attributes, {
            class: `${attributes.class} ${this.config.classNames.control}`
          });
        }
      } else {
        attributes.class = this.config.classNames.control;
      }

      // Large play button
      switch (buttonType) {
        case 'play':
          props.toggle = true;
          props.label = 'play';
          props.labelPressed = 'pause';
          props.icon = 'play';
          props.iconPressed = 'pause';
          break;
        case 'mute':
          props.toggle = true;
          props.label = 'mute';
          props.labelPressed = 'unmute';
          props.icon = 'volume';
          props.iconPressed = 'muted';
          break;
        case 'captions':
          props.toggle = true;
          props.label = 'enableCaptions';
          props.labelPressed = 'disableCaptions';
          props.icon = 'captions-off';
          props.iconPressed = 'captions-on';
          break;
        case 'fullscreen':
          props.toggle = true;
          props.label = 'enterFullscreen';
          props.labelPressed = 'exitFullscreen';
          props.icon = 'enter-fullscreen';
          props.iconPressed = 'exit-fullscreen';
          break;
        case 'play-large':
          attributes.class += ` ${this.config.classNames.control}--overlaid`;
          type = 'play';
          props.label = 'play';
          props.icon = 'play';
          break;
        default:
          if (is.empty(props.label)) {
            props.label = type;
          }
          if (is.empty(props.icon)) {
            props.icon = buttonType;
          }
      }
      const button = createElement(props.element);

      // Setup toggle icon and labels
      if (props.toggle) {
        // Icon
        button.appendChild(controls.createIcon.call(this, props.iconPressed, {
          class: 'icon--pressed'
        }));
        button.appendChild(controls.createIcon.call(this, props.icon, {
          class: 'icon--not-pressed'
        }));

        // Label/Tooltip
        button.appendChild(controls.createLabel.call(this, props.labelPressed, {
          class: 'label--pressed'
        }));
        button.appendChild(controls.createLabel.call(this, props.label, {
          class: 'label--not-pressed'
        }));
      } else {
        button.appendChild(controls.createIcon.call(this, props.icon));
        button.appendChild(controls.createLabel.call(this, props.label));
      }

      // Merge and set attributes
      extend(attributes, getAttributesFromSelector(this.config.selectors.buttons[type], attributes));
      setAttributes(button, attributes);

      // We have multiple play buttons
      if (type === 'play') {
        if (!is.array(this.elements.buttons[type])) {
          this.elements.buttons[type] = [];
        }
        this.elements.buttons[type].push(button);
      } else {
        this.elements.buttons[type] = button;
      }
      return button;
    },
    // Create an <input type='range'>
    createRange(type, attributes) {
      // Seek input
      const input = createElement('input', extend(getAttributesFromSelector(this.config.selectors.inputs[type]), {
        type: 'range',
        min: 0,
        max: 100,
        step: 0.01,
        value: 0,
        autocomplete: 'off',
        // A11y fixes for https://github.com/sampotts/plyr/issues/905
        role: 'slider',
        'aria-label': i18n.get(type, this.config),
        'aria-valuemin': 0,
        'aria-valuemax': 100,
        'aria-valuenow': 0
      }, attributes));
      this.elements.inputs[type] = input;

      // Set the fill for webkit now
      controls.updateRangeFill.call(this, input);

      // Improve support on touch devices
      RangeTouch.setup(input);
      return input;
    },
    // Create a <progress>
    createProgress(type, attributes) {
      const progress = createElement('progress', extend(getAttributesFromSelector(this.config.selectors.display[type]), {
        min: 0,
        max: 100,
        value: 0,
        role: 'progressbar',
        'aria-hidden': true
      }, attributes));

      // Create the label inside
      if (type !== 'volume') {
        progress.appendChild(createElement('span', null, '0'));
        const suffixKey = {
          played: 'played',
          buffer: 'buffered'
        }[type];
        const suffix = suffixKey ? i18n.get(suffixKey, this.config) : '';
        progress.innerText = `% ${suffix.toLowerCase()}`;
      }
      this.elements.display[type] = progress;
      return progress;
    },
    // Create time display
    createTime(type, attrs) {
      const attributes = getAttributesFromSelector(this.config.selectors.display[type], attrs);
      const container = createElement('div', extend(attributes, {
        class: `${attributes.class ? attributes.class : ''} ${this.config.classNames.display.time} `.trim(),
        'aria-label': i18n.get(type, this.config),
        role: 'timer'
      }), '00:00');

      // Reference for updates
      this.elements.display[type] = container;
      return container;
    },
    // Bind keyboard shortcuts for a menu item
    // We have to bind to keyup otherwise Firefox triggers a click when a keydown event handler shifts focus
    // https://bugzilla.mozilla.org/show_bug.cgi?id=1220143
    bindMenuItemShortcuts(menuItem, type) {
      // Navigate through menus via arrow keys and space
      on.call(this, menuItem, 'keydown keyup', event => {
        // We only care about space and ⬆️ ⬇️️ ➡️
        if (![' ', 'ArrowUp', 'ArrowDown', 'ArrowRight'].includes(event.key)) {
          return;
        }

        // Prevent play / seek
        event.preventDefault();
        event.stopPropagation();

        // We're just here to prevent the keydown bubbling
        if (event.type === 'keydown') {
          return;
        }
        const isRadioButton = matches(menuItem, '[role="menuitemradio"]');

        // Show the respective menu
        if (!isRadioButton && [' ', 'ArrowRight'].includes(event.key)) {
          controls.showMenuPanel.call(this, type, true);
        } else {
          let target;
          if (event.key !== ' ') {
            if (event.key === 'ArrowDown' || isRadioButton && event.key === 'ArrowRight') {
              target = menuItem.nextElementSibling;
              if (!is.element(target)) {
                target = menuItem.parentNode.firstElementChild;
              }
            } else {
              target = menuItem.previousElementSibling;
              if (!is.element(target)) {
                target = menuItem.parentNode.lastElementChild;
              }
            }
            setFocus.call(this, target, true);
          }
        }
      }, false);

      // Enter will fire a `click` event but we still need to manage focus
      // So we bind to keyup which fires after and set focus here
      on.call(this, menuItem, 'keyup', event => {
        if (event.key !== 'Return') return;
        controls.focusFirstMenuItem.call(this, null, true);
      });
    },
    // Create a settings menu item
    createMenuItem({
      value,
      list,
      type,
      title,
      badge = null,
      checked = false
    }) {
      const attributes = getAttributesFromSelector(this.config.selectors.inputs[type]);
      const menuItem = createElement('button', extend(attributes, {
        type: 'button',
        role: 'menuitemradio',
        class: `${this.config.classNames.control} ${attributes.class ? attributes.class : ''}`.trim(),
        'aria-checked': checked,
        value
      }));
      const flex = createElement('span');

      // We have to set as HTML incase of special characters
      flex.innerHTML = title;
      if (is.element(badge)) {
        flex.appendChild(badge);
      }
      menuItem.appendChild(flex);

      // Replicate radio button behavior
      Object.defineProperty(menuItem, 'checked', {
        enumerable: true,
        get() {
          return menuItem.getAttribute('aria-checked') === 'true';
        },
        set(check) {
          // Ensure exclusivity
          if (check) {
            Array.from(menuItem.parentNode.children).filter(node => matches(node, '[role="menuitemradio"]')).forEach(node => node.setAttribute('aria-checked', 'false'));
          }
          menuItem.setAttribute('aria-checked', check ? 'true' : 'false');
        }
      });
      this.listeners.bind(menuItem, 'click keyup', event => {
        if (is.keyboardEvent(event) && event.key !== ' ') {
          return;
        }
        event.preventDefault();
        event.stopPropagation();
        menuItem.checked = true;
        switch (type) {
          case 'language':
            this.currentTrack = Number(value);
            break;
          case 'quality':
            this.quality = value;
            break;
          case 'speed':
            this.speed = parseFloat(value);
            break;
        }
        controls.showMenuPanel.call(this, 'home', is.keyboardEvent(event));
      }, type, false);
      controls.bindMenuItemShortcuts.call(this, menuItem, type);
      list.appendChild(menuItem);
    },
    // Format a time for display
    formatTime(time = 0, inverted = false) {
      // Bail if the value isn't a number
      if (!is.number(time)) {
        return time;
      }

      // Always display hours if duration is over an hour
      const forceHours = getHours(this.duration) > 0;
      return formatTime(time, forceHours, inverted);
    },
    // Update the displayed time
    updateTimeDisplay(target = null, time = 0, inverted = false) {
      // Bail if there's no element to display or the value isn't a number
      if (!is.element(target) || !is.number(time)) {
        return;
      }

      // eslint-disable-next-line no-param-reassign
      target.innerText = controls.formatTime(time, inverted);
    },
    // Update volume UI and storage
    updateVolume() {
      if (!this.supported.ui) {
        return;
      }

      // Update range
      if (is.element(this.elements.inputs.volume)) {
        controls.setRange.call(this, this.elements.inputs.volume, this.muted ? 0 : this.volume);
      }

      // Update mute state
      if (is.element(this.elements.buttons.mute)) {
        this.elements.buttons.mute.pressed = this.muted || this.volume === 0;
      }
    },
    // Update seek value and lower fill
    setRange(target, value = 0) {
      if (!is.element(target)) {
        return;
      }

      // eslint-disable-next-line
      target.value = value;

      // Webkit range fill
      controls.updateRangeFill.call(this, target);
    },
    // Update <progress> elements
    updateProgress(event) {
      if (!this.supported.ui || !is.event(event)) {
        return;
      }
      let value = 0;
      const setProgress = (target, input) => {
        const val = is.number(input) ? input : 0;
        const progress = is.element(target) ? target : this.elements.display.buffer;

        // Update value and label
        if (is.element(progress)) {
          progress.value = val;

          // Update text label inside
          const label = progress.getElementsByTagName('span')[0];
          if (is.element(label)) {
            label.childNodes[0].nodeValue = val;
          }
        }
      };
      if (event) {
        switch (event.type) {
          // Video playing
          case 'timeupdate':
          case 'seeking':
          case 'seeked':
            value = getPercentage(this.currentTime, this.duration);

            // Set seek range value only if it's a 'natural' time event
            if (event.type === 'timeupdate') {
              controls.setRange.call(this, this.elements.inputs.seek, value);
            }
            break;

          // Check buffer status
          case 'playing':
          case 'progress':
            setProgress(this.elements.display.buffer, this.buffered * 100);
            break;
        }
      }
    },
    // Webkit polyfill for lower fill range
    updateRangeFill(target) {
      // Get range from event if event passed
      const range = is.event(target) ? target.target : target;

      // Needs to be a valid <input type='range'>
      if (!is.element(range) || range.getAttribute('type') !== 'range') {
        return;
      }

      // Set aria values for https://github.com/sampotts/plyr/issues/905
      if (matches(range, this.config.selectors.inputs.seek)) {
        range.setAttribute('aria-valuenow', this.currentTime);
        const currentTime = controls.formatTime(this.currentTime);
        const duration = controls.formatTime(this.duration);
        const format = i18n.get('seekLabel', this.config);
        range.setAttribute('aria-valuetext', format.replace('{currentTime}', currentTime).replace('{duration}', duration));
      } else if (matches(range, this.config.selectors.inputs.volume)) {
        const percent = range.value * 100;
        range.setAttribute('aria-valuenow', percent);
        range.setAttribute('aria-valuetext', `${percent.toFixed(1)}%`);
      } else {
        range.setAttribute('aria-valuenow', range.value);
      }

      // WebKit only
      if (!browser.isWebKit && !browser.isIPadOS) {
        return;
      }

      // Set CSS custom property
      range.style.setProperty('--value', `${range.value / range.max * 100}%`);
    },
    // Update hover tooltip for seeking
    updateSeekTooltip(event) {
      var _this$config$markers, _this$config$markers$;
      // Bail if setting not true
      if (!this.config.tooltips.seek || !is.element(this.elements.inputs.seek) || !is.element(this.elements.display.seekTooltip) || this.duration === 0) {
        return;
      }
      const tipElement = this.elements.display.seekTooltip;
      const visible = `${this.config.classNames.tooltip}--visible`;
      const toggle = show => toggleClass(tipElement, visible, show);

      // Hide on touch
      if (this.touch) {
        toggle(false);
        return;
      }

      // Determine percentage, if already visible
      let percent = 0;
      const clientRect = this.elements.progress.getBoundingClientRect();
      if (is.event(event)) {
        percent = 100 / clientRect.width * (event.pageX - clientRect.left);
      } else if (hasClass(tipElement, visible)) {
        percent = parseFloat(tipElement.style.left, 10);
      } else {
        return;
      }

      // Set bounds
      if (percent < 0) {
        percent = 0;
      } else if (percent > 100) {
        percent = 100;
      }
      const time = this.duration / 100 * percent;

      // Display the time a click would seek to
      tipElement.innerText = controls.formatTime(time);

      // Get marker point for time
      const point = (_this$config$markers = this.config.markers) === null || _this$config$markers === void 0 ? void 0 : (_this$config$markers$ = _this$config$markers.points) === null || _this$config$markers$ === void 0 ? void 0 : _this$config$markers$.find(({
        time: t
      }) => t === Math.round(time));

      // Append the point label to the tooltip
      if (point) {
        tipElement.insertAdjacentHTML('afterbegin', `${point.label}<br>`);
      }

      // Set position
      tipElement.style.left = `${percent}%`;

      // Show/hide the tooltip
      // If the event is a moues in/out and percentage is inside bounds
      if (is.event(event) && ['mouseenter', 'mouseleave'].includes(event.type)) {
        toggle(event.type === 'mouseenter');
      }
    },
    // Handle time change event
    timeUpdate(event) {
      // Only invert if only one time element is displayed and used for both duration and currentTime
      const invert = !is.element(this.elements.display.duration) && this.config.invertTime;

      // Duration
      controls.updateTimeDisplay.call(this, this.elements.display.currentTime, invert ? this.duration - this.currentTime : this.currentTime, invert);

      // Ignore updates while seeking
      if (event && event.type === 'timeupdate' && this.media.seeking) {
        return;
      }

      // Playing progress
      controls.updateProgress.call(this, event);
    },
    // Show the duration on metadataloaded or durationchange events
    durationUpdate() {
      // Bail if no UI or durationchange event triggered after playing/seek when invertTime is false
      if (!this.supported.ui || !this.config.invertTime && this.currentTime) {
        return;
      }

      // If duration is the 2**32 (shaka), Infinity (HLS), DASH-IF (Number.MAX_SAFE_INTEGER || Number.MAX_VALUE) indicating live we hide the currentTime and progressbar.
      // https://github.com/video-dev/hls.js/blob/5820d29d3c4c8a46e8b75f1e3afa3e68c1a9a2db/src/controller/buffer-controller.js#L415
      // https://github.com/google/shaka-player/blob/4d889054631f4e1cf0fbd80ddd2b71887c02e232/lib/media/streaming_engine.js#L1062
      // https://github.com/Dash-Industry-Forum/dash.js/blob/69859f51b969645b234666800d4cb596d89c602d/src/dash/models/DashManifestModel.js#L338
      if (this.duration >= 2 ** 32) {
        toggleHidden(this.elements.display.currentTime, true);
        toggleHidden(this.elements.progress, true);
        return;
      }

      // Update ARIA values
      if (is.element(this.elements.inputs.seek)) {
        this.elements.inputs.seek.setAttribute('aria-valuemax', this.duration);
      }

      // If there's a spot to display duration
      const hasDuration = is.element(this.elements.display.duration);

      // If there's only one time display, display duration there
      if (!hasDuration && this.config.displayDuration && this.paused) {
        controls.updateTimeDisplay.call(this, this.elements.display.currentTime, this.duration);
      }

      // If there's a duration element, update content
      if (hasDuration) {
        controls.updateTimeDisplay.call(this, this.elements.display.duration, this.duration);
      }
      if (this.config.markers.enabled) {
        controls.setMarkers.call(this);
      }

      // Update the tooltip (if visible)
      controls.updateSeekTooltip.call(this);
    },
    // Hide/show a tab
    toggleMenuButton(setting, toggle) {
      toggleHidden(this.elements.settings.buttons[setting], !toggle);
    },
    // Update the selected setting
    updateSetting(setting, container, input) {
      const pane = this.elements.settings.panels[setting];
      let value = null;
      let list = container;
      if (setting === 'captions') {
        value = this.currentTrack;
      } else {
        value = !is.empty(input) ? input : this[setting];

        // Get default
        if (is.empty(value)) {
          value = this.config[setting].default;
        }

        // Unsupported value
        if (!is.empty(this.options[setting]) && !this.options[setting].includes(value)) {
          this.debug.warn(`Unsupported value of '${value}' for ${setting}`);
          return;
        }

        // Disabled value
        if (!this.config[setting].options.includes(value)) {
          this.debug.warn(`Disabled value of '${value}' for ${setting}`);
          return;
        }
      }

      // Get the list if we need to
      if (!is.element(list)) {
        list = pane && pane.querySelector('[role="menu"]');
      }

      // If there's no list it means it's not been rendered...
      if (!is.element(list)) {
        return;
      }

      // Update the label
      const label = this.elements.settings.buttons[setting].querySelector(`.${this.config.classNames.menu.value}`);
      label.innerHTML = controls.getLabel.call(this, setting, value);

      // Find the radio option and check it
      const target = list && list.querySelector(`[value="${value}"]`);
      if (is.element(target)) {
        target.checked = true;
      }
    },
    // Translate a value into a nice label
    getLabel(setting, value) {
      switch (setting) {
        case 'speed':
          return value === 1 ? i18n.get('normal', this.config) : `${value}&times;`;
        case 'quality':
          if (is.number(value)) {
            const label = i18n.get(`qualityLabel.${value}`, this.config);
            if (!label.length) {
              return `${value}p`;
            }
            return label;
          }
          return toTitleCase(value);
        case 'captions':
          return captions.getLabel.call(this);
        default:
          return null;
      }
    },
    // Set the quality menu
    setQualityMenu(options) {
      // Menu required
      if (!is.element(this.elements.settings.panels.quality)) {
        return;
      }
      const type = 'quality';
      const list = this.elements.settings.panels.quality.querySelector('[role="menu"]');

      // Set options if passed and filter based on uniqueness and config
      if (is.array(options)) {
        this.options.quality = dedupe(options).filter(quality => this.config.quality.options.includes(quality));
      }

      // Toggle the pane and tab
      const toggle = !is.empty(this.options.quality) && this.options.quality.length > 1;
      controls.toggleMenuButton.call(this, type, toggle);

      // Empty the menu
      emptyElement(list);

      // Check if we need to toggle the parent
      controls.checkMenu.call(this);

      // If we're hiding, nothing more to do
      if (!toggle) {
        return;
      }

      // Get the badge HTML for HD, 4K etc
      const getBadge = quality => {
        const label = i18n.get(`qualityBadge.${quality}`, this.config);
        if (!label.length) {
          return null;
        }
        return controls.createBadge.call(this, label);
      };

      // Sort options by the config and then render options
      this.options.quality.sort((a, b) => {
        const sorting = this.config.quality.options;
        return sorting.indexOf(a) > sorting.indexOf(b) ? 1 : -1;
      }).forEach(quality => {
        controls.createMenuItem.call(this, {
          value: quality,
          list,
          type,
          title: controls.getLabel.call(this, 'quality', quality),
          badge: getBadge(quality)
        });
      });
      controls.updateSetting.call(this, type, list);
    },
    // Set the looping options
    /* setLoopMenu() {
          // Menu required
          if (!is.element(this.elements.settings.panels.loop)) {
              return;
          }
           const options = ['start', 'end', 'all', 'reset'];
          const list = this.elements.settings.panels.loop.querySelector('[role="menu"]');
           // Show the pane and tab
          toggleHidden(this.elements.settings.buttons.loop, false);
          toggleHidden(this.elements.settings.panels.loop, false);
           // Toggle the pane and tab
          const toggle = !is.empty(this.loop.options);
          controls.toggleMenuButton.call(this, 'loop', toggle);
           // Empty the menu
          emptyElement(list);
           options.forEach(option => {
              const item = createElement('li');
               const button = createElement(
                  'button',
                  extend(getAttributesFromSelector(this.config.selectors.buttons.loop), {
                      type: 'button',
                      class: this.config.classNames.control,
                      'data-plyr-loop-action': option,
                  }),
                  i18n.get(option, this.config)
              );
               if (['start', 'end'].includes(option)) {
                  const badge = controls.createBadge.call(this, '00:00');
                  button.appendChild(badge);
              }
               item.appendChild(button);
              list.appendChild(item);
          });
      }, */

    // Get current selected caption language
    // TODO: rework this to user the getter in the API?

    // Set a list of available captions languages
    setCaptionsMenu() {
      // Menu required
      if (!is.element(this.elements.settings.panels.captions)) {
        return;
      }

      // TODO: Captions or language? Currently it's mixed
      const type = 'captions';
      const list = this.elements.settings.panels.captions.querySelector('[role="menu"]');
      const tracks = captions.getTracks.call(this);
      const toggle = Boolean(tracks.length);

      // Toggle the pane and tab
      controls.toggleMenuButton.call(this, type, toggle);

      // Empty the menu
      emptyElement(list);

      // Check if we need to toggle the parent
      controls.checkMenu.call(this);

      // If there's no captions, bail
      if (!toggle) {
        return;
      }

      // Generate options data
      const options = tracks.map((track, value) => ({
        value,
        checked: this.captions.toggled && this.currentTrack === value,
        title: captions.getLabel.call(this, track),
        badge: track.language && controls.createBadge.call(this, track.language.toUpperCase()),
        list,
        type: 'language'
      }));

      // Add the "Disabled" option to turn off captions
      options.unshift({
        value: -1,
        checked: !this.captions.toggled,
        title: i18n.get('disabled', this.config),
        list,
        type: 'language'
      });

      // Generate options
      options.forEach(controls.createMenuItem.bind(this));
      controls.updateSetting.call(this, type, list);
    },
    // Set a list of available captions languages
    setSpeedMenu() {
      // Menu required
      if (!is.element(this.elements.settings.panels.speed)) {
        return;
      }
      const type = 'speed';
      const list = this.elements.settings.panels.speed.querySelector('[role="menu"]');

      // Filter out invalid speeds
      this.options.speed = this.options.speed.filter(o => o >= this.minimumSpeed && o <= this.maximumSpeed);

      // Toggle the pane and tab
      const toggle = !is.empty(this.options.speed) && this.options.speed.length > 1;
      controls.toggleMenuButton.call(this, type, toggle);

      // Empty the menu
      emptyElement(list);

      // Check if we need to toggle the parent
      controls.checkMenu.call(this);

      // If we're hiding, nothing more to do
      if (!toggle) {
        return;
      }

      // Create items
      this.options.speed.forEach(speed => {
        controls.createMenuItem.call(this, {
          value: speed,
          list,
          type,
          title: controls.getLabel.call(this, 'speed', speed)
        });
      });
      controls.updateSetting.call(this, type, list);
    },
    // Check if we need to hide/show the settings menu
    checkMenu() {
      const {
        buttons
      } = this.elements.settings;
      const visible = !is.empty(buttons) && Object.values(buttons).some(button => !button.hidden);
      toggleHidden(this.elements.settings.menu, !visible);
    },
    // Focus the first menu item in a given (or visible) menu
    focusFirstMenuItem(pane, focusVisible = false) {
      if (this.elements.settings.popup.hidden) {
        return;
      }
      let target = pane;
      if (!is.element(target)) {
        target = Object.values(this.elements.settings.panels).find(p => !p.hidden);
      }
      const firstItem = target.querySelector('[role^="menuitem"]');
      setFocus.call(this, firstItem, focusVisible);
    },
    // Show/hide menu
    toggleMenu(input) {
      const {
        popup
      } = this.elements.settings;
      const button = this.elements.buttons.settings;

      // Menu and button are required
      if (!is.element(popup) || !is.element(button)) {
        return;
      }

      // True toggle by default
      const {
        hidden
      } = popup;
      let show = hidden;
      if (is.boolean(input)) {
        show = input;
      } else if (is.keyboardEvent(input) && input.key === 'Escape') {
        show = false;
      } else if (is.event(input)) {
        // If Plyr is in a shadowDOM, the event target is set to the component, instead of the
        // Element in the shadowDOM. The path, if available, is complete.
        const target = is.function(input.composedPath) ? input.composedPath()[0] : input.target;
        const isMenuItem = popup.contains(target);

        // If the click was inside the menu or if the click
        // wasn't the button or menu item and we're trying to
        // show the menu (a doc click shouldn't show the menu)
        if (isMenuItem || !isMenuItem && input.target !== button && show) {
          return;
        }
      }

      // Set button attributes
      button.setAttribute('aria-expanded', show);

      // Show the actual popup
      toggleHidden(popup, !show);

      // Add class hook
      toggleClass(this.elements.container, this.config.classNames.menu.open, show);

      // Focus the first item if key interaction
      if (show && is.keyboardEvent(input)) {
        controls.focusFirstMenuItem.call(this, null, true);
      } else if (!show && !hidden) {
        // If closing, re-focus the button
        setFocus.call(this, button, is.keyboardEvent(input));
      }
    },
    // Get the natural size of a menu panel
    getMenuSize(tab) {
      const clone = tab.cloneNode(true);
      clone.style.position = 'absolute';
      clone.style.opacity = 0;
      clone.removeAttribute('hidden');

      // Append to parent so we get the "real" size
      tab.parentNode.appendChild(clone);

      // Get the sizes before we remove
      const width = clone.scrollWidth;
      const height = clone.scrollHeight;

      // Remove from the DOM
      removeElement(clone);
      return {
        width,
        height
      };
    },
    // Show a panel in the menu
    showMenuPanel(type = '', focusVisible = false) {
      const target = this.elements.container.querySelector(`#plyr-settings-${this.id}-${type}`);

      // Nothing to show, bail
      if (!is.element(target)) {
        return;
      }

      // Hide all other panels
      const container = target.parentNode;
      const current = Array.from(container.children).find(node => !node.hidden);

      // If we can do fancy animations, we'll animate the height/width
      if (support.transitions && !support.reducedMotion) {
        // Set the current width as a base
        container.style.width = `${current.scrollWidth}px`;
        container.style.height = `${current.scrollHeight}px`;

        // Get potential sizes
        const size = controls.getMenuSize.call(this, target);

        // Restore auto height/width
        const restore = event => {
          // We're only bothered about height and width on the container
          if (event.target !== container || !['width', 'height'].includes(event.propertyName)) {
            return;
          }

          // Revert back to auto
          container.style.width = '';
          container.style.height = '';

          // Only listen once
          off.call(this, container, transitionEndEvent, restore);
        };

        // Listen for the transition finishing and restore auto height/width
        on.call(this, container, transitionEndEvent, restore);

        // Set dimensions to target
        container.style.width = `${size.width}px`;
        container.style.height = `${size.height}px`;
      }

      // Set attributes on current tab
      toggleHidden(current, true);

      // Set attributes on target
      toggleHidden(target, false);

      // Focus the first item
      controls.focusFirstMenuItem.call(this, target, focusVisible);
    },
    // Set the download URL
    setDownloadUrl() {
      const button = this.elements.buttons.download;

      // Bail if no button
      if (!is.element(button)) {
        return;
      }

      // Set attribute
      button.setAttribute('href', this.download);
    },
    // Build the default HTML
    create(data) {
      const {
        bindMenuItemShortcuts,
        createButton,
        createProgress,
        createRange,
        createTime,
        setQualityMenu,
        setSpeedMenu,
        showMenuPanel
      } = controls;
      this.elements.controls = null;

      // Larger overlaid play button
      if (is.array(this.config.controls) && this.config.controls.includes('play-large')) {
        this.elements.container.appendChild(createButton.call(this, 'play-large'));
      }

      // Create the container
      const container = createElement('div', getAttributesFromSelector(this.config.selectors.controls.wrapper));
      this.elements.controls = container;

      // Default item attributes
      const defaultAttributes = {
        class: 'plyr__controls__item'
      };

      // Loop through controls in order
      dedupe(is.array(this.config.controls) ? this.config.controls : []).forEach(control => {
        // Restart button
        if (control === 'restart') {
          container.appendChild(createButton.call(this, 'restart', defaultAttributes));
        }

        // Rewind button
        if (control === 'rewind') {
          container.appendChild(createButton.call(this, 'rewind', defaultAttributes));
        }

        // Play/Pause button
        if (control === 'play') {
          container.appendChild(createButton.call(this, 'play', defaultAttributes));
        }

        // Fast forward button
        if (control === 'fast-forward') {
          container.appendChild(createButton.call(this, 'fast-forward', defaultAttributes));
        }

        // Progress
        if (control === 'progress') {
          const progressContainer = createElement('div', {
            class: `${defaultAttributes.class} plyr__progress__container`
          });
          const progress = createElement('div', getAttributesFromSelector(this.config.selectors.progress));

          // Seek range slider
          progress.appendChild(createRange.call(this, 'seek', {
            id: `plyr-seek-${data.id}`
          }));

          // Buffer progress
          progress.appendChild(createProgress.call(this, 'buffer'));

          // TODO: Add loop display indicator

          // Seek tooltip
          if (this.config.tooltips.seek) {
            const tooltip = createElement('span', {
              class: this.config.classNames.tooltip
            }, '00:00');
            progress.appendChild(tooltip);
            this.elements.display.seekTooltip = tooltip;
          }
          this.elements.progress = progress;
          progressContainer.appendChild(this.elements.progress);
          container.appendChild(progressContainer);
        }

        // Media current time display
        if (control === 'current-time') {
          container.appendChild(createTime.call(this, 'currentTime', defaultAttributes));
        }

        // Media duration display
        if (control === 'duration') {
          container.appendChild(createTime.call(this, 'duration', defaultAttributes));
        }

        // Volume controls
        if (control === 'mute' || control === 'volume') {
          let {
            volume
          } = this.elements;

          // Create the volume container if needed
          if (!is.element(volume) || !container.contains(volume)) {
            volume = createElement('div', extend({}, defaultAttributes, {
              class: `${defaultAttributes.class} plyr__volume`.trim()
            }));
            this.elements.volume = volume;
            container.appendChild(volume);
          }

          // Toggle mute button
          if (control === 'mute') {
            volume.appendChild(createButton.call(this, 'mute'));
          }

          // Volume range control
          // Ignored on iOS as it's handled globally
          // https://developer.apple.com/library/safari/documentation/AudioVideo/Conceptual/Using_HTML5_Audio_Video/Device-SpecificConsiderations/Device-SpecificConsiderations.html
          if (control === 'volume' && !browser.isIos && !browser.isIPadOS) {
            // Set the attributes
            const attributes = {
              max: 1,
              step: 0.05,
              value: this.config.volume
            };

            // Create the volume range slider
            volume.appendChild(createRange.call(this, 'volume', extend(attributes, {
              id: `plyr-volume-${data.id}`
            })));
          }
        }

        // Toggle captions button
        if (control === 'captions') {
          container.appendChild(createButton.call(this, 'captions', defaultAttributes));
        }

        // Settings button / menu
        if (control === 'settings' && !is.empty(this.config.settings)) {
          const wrapper = createElement('div', extend({}, defaultAttributes, {
            class: `${defaultAttributes.class} plyr__menu`.trim(),
            hidden: ''
          }));
          wrapper.appendChild(createButton.call(this, 'settings', {
            'aria-haspopup': true,
            'aria-controls': `plyr-settings-${data.id}`,
            'aria-expanded': false
          }));
          const popup = createElement('div', {
            class: 'plyr__menu__container',
            id: `plyr-settings-${data.id}`,
            hidden: ''
          });
          const inner = createElement('div');
          const home = createElement('div', {
            id: `plyr-settings-${data.id}-home`
          });

          // Create the menu
          const menu = createElement('div', {
            role: 'menu'
          });
          home.appendChild(menu);
          inner.appendChild(home);
          this.elements.settings.panels.home = home;

          // Build the menu items
          this.config.settings.forEach(type => {
            // TODO: bundle this with the createMenuItem helper and bindings
            const menuItem = createElement('button', extend(getAttributesFromSelector(this.config.selectors.buttons.settings), {
              type: 'button',
              class: `${this.config.classNames.control} ${this.config.classNames.control}--forward`,
              role: 'menuitem',
              'aria-haspopup': true,
              hidden: ''
            }));

            // Bind menu shortcuts for keyboard users
            bindMenuItemShortcuts.call(this, menuItem, type);

            // Show menu on click
            on.call(this, menuItem, 'click', () => {
              showMenuPanel.call(this, type, false);
            });
            const flex = createElement('span', null, i18n.get(type, this.config));
            const value = createElement('span', {
              class: this.config.classNames.menu.value
            });

            // Speed contains HTML entities
            value.innerHTML = data[type];
            flex.appendChild(value);
            menuItem.appendChild(flex);
            menu.appendChild(menuItem);

            // Build the panes
            const pane = createElement('div', {
              id: `plyr-settings-${data.id}-${type}`,
              hidden: ''
            });

            // Back button
            const backButton = createElement('button', {
              type: 'button',
              class: `${this.config.classNames.control} ${this.config.classNames.control}--back`
            });

            // Visible label
            backButton.appendChild(createElement('span', {
              'aria-hidden': true
            }, i18n.get(type, this.config)));

            // Screen reader label
            backButton.appendChild(createElement('span', {
              class: this.config.classNames.hidden
            }, i18n.get('menuBack', this.config)));

            // Go back via keyboard
            on.call(this, pane, 'keydown', event => {
              if (event.key !== 'ArrowLeft') return;

              // Prevent seek
              event.preventDefault();
              event.stopPropagation();

              // Show the respective menu
              showMenuPanel.call(this, 'home', true);
            }, false);

            // Go back via button click
            on.call(this, backButton, 'click', () => {
              showMenuPanel.call(this, 'home', false);
            });

            // Add to pane
            pane.appendChild(backButton);

            // Menu
            pane.appendChild(createElement('div', {
              role: 'menu'
            }));
            inner.appendChild(pane);
            this.elements.settings.buttons[type] = menuItem;
            this.elements.settings.panels[type] = pane;
          });
          popup.appendChild(inner);
          wrapper.appendChild(popup);
          container.appendChild(wrapper);
          this.elements.settings.popup = popup;
          this.elements.settings.menu = wrapper;
        }

        // Picture in picture button
        if (control === 'pip' && support.pip) {
          container.appendChild(createButton.call(this, 'pip', defaultAttributes));
        }

        // Airplay button
        if (control === 'airplay' && support.airplay) {
          container.appendChild(createButton.call(this, 'airplay', defaultAttributes));
        }

        // Download button
        if (control === 'download') {
          const attributes = extend({}, defaultAttributes, {
            element: 'a',
            href: this.download,
            target: '_blank'
          });

          // Set download attribute for HTML5 only
          if (this.isHTML5) {
            attributes.download = '';
          }
          const {
            download
          } = this.config.urls;
          if (!is.url(download) && this.isEmbed) {
            extend(attributes, {
              icon: `logo-${this.provider}`,
              label: this.provider
            });
          }
          container.appendChild(createButton.call(this, 'download', attributes));
        }

        // Toggle fullscreen button
        if (control === 'fullscreen') {
          container.appendChild(createButton.call(this, 'fullscreen', defaultAttributes));
        }
      });

      // Set available quality levels
      if (this.isHTML5) {
        setQualityMenu.call(this, html5.getQualityOptions.call(this));
      }
      setSpeedMenu.call(this);
      return container;
    },
    // Insert controls
    inject() {
      // Sprite
      if (this.config.loadSprite) {
        const icon = controls.getIconUrl.call(this);

        // Only load external sprite using AJAX
        if (icon.cors) {
          loadSprite(icon.url, 'sprite-plyr');
        }
      }

      // Create a unique ID
      this.id = Math.floor(Math.random() * 10000);

      // Null by default
      let container = null;
      this.elements.controls = null;

      // Set template properties
      const props = {
        id: this.id,
        seektime: this.config.seekTime,
        title: this.config.title
      };
      let update = true;

      // If function, run it and use output
      if (is.function(this.config.controls)) {
        this.config.controls = this.config.controls.call(this, props);
      }

      // Convert falsy controls to empty array (primarily for empty strings)
      if (!this.config.controls) {
        this.config.controls = [];
      }
      if (is.element(this.config.controls) || is.string(this.config.controls)) {
        // HTMLElement or Non-empty string passed as the option
        container = this.config.controls;
      } else {
        // Create controls
        container = controls.create.call(this, {
          id: this.id,
          seektime: this.config.seekTime,
          speed: this.speed,
          quality: this.quality,
          captions: captions.getLabel.call(this)
          // TODO: Looping
          // loop: 'None',
        });

        update = false;
      }

      // Replace props with their value
      const replace = input => {
        let result = input;
        Object.entries(props).forEach(([key, value]) => {
          result = replaceAll(result, `{${key}}`, value);
        });
        return result;
      };

      // Update markup
      if (update) {
        if (is.string(this.config.controls)) {
          container = replace(container);
        }
      }

      // Controls container
      let target;

      // Inject to custom location
      if (is.string(this.config.selectors.controls.container)) {
        target = document.querySelector(this.config.selectors.controls.container);
      }

      // Inject into the container by default
      if (!is.element(target)) {
        target = this.elements.container;
      }

      // Inject controls HTML (needs to be before captions, hence "afterbegin")
      const insertMethod = is.element(container) ? 'insertAdjacentElement' : 'insertAdjacentHTML';
      target[insertMethod]('afterbegin', container);

      // Find the elements if need be
      if (!is.element(this.elements.controls)) {
        controls.findElements.call(this);
      }

      // Add pressed property to buttons
      if (!is.empty(this.elements.buttons)) {
        const addProperty = button => {
          const className = this.config.classNames.controlPressed;
          button.setAttribute('aria-pressed', 'false');
          Object.defineProperty(button, 'pressed', {
            configurable: true,
            enumerable: true,
            get() {
              return hasClass(button, className);
            },
            set(pressed = false) {
              toggleClass(button, className, pressed);
              button.setAttribute('aria-pressed', pressed ? 'true' : 'false');
            }
          });
        };

        // Toggle classname when pressed property is set
        Object.values(this.elements.buttons).filter(Boolean).forEach(button => {
          if (is.array(button) || is.nodeList(button)) {
            Array.from(button).filter(Boolean).forEach(addProperty);
          } else {
            addProperty(button);
          }
        });
      }

      // Edge sometimes doesn't finish the paint so force a repaint
      if (browser.isEdge) {
        repaint(target);
      }

      // Setup tooltips
      if (this.config.tooltips.controls) {
        const {
          classNames,
          selectors
        } = this.config;
        const selector = `${selectors.controls.wrapper} ${selectors.labels} .${classNames.hidden}`;
        const labels = getElements.call(this, selector);
        Array.from(labels).forEach(label => {
          toggleClass(label, this.config.classNames.hidden, false);
          toggleClass(label, this.config.classNames.tooltip, true);
        });
      }
    },
    // Set media metadata
    setMediaMetadata() {
      try {
        if ('mediaSession' in navigator) {
          navigator.mediaSession.metadata = new window.MediaMetadata({
            title: this.config.mediaMetadata.title,
            artist: this.config.mediaMetadata.artist,
            album: this.config.mediaMetadata.album,
            artwork: this.config.mediaMetadata.artwork
          });
        }
      } catch (_) {
        // Do nothing
      }
    },
    // Add markers
    setMarkers() {
      var _this$config$markers2, _this$config$markers3;
      if (!this.duration || this.elements.markers) return;

      // Get valid points
      const points = (_this$config$markers2 = this.config.markers) === null || _this$config$markers2 === void 0 ? void 0 : (_this$config$markers3 = _this$config$markers2.points) === null || _this$config$markers3 === void 0 ? void 0 : _this$config$markers3.filter(({
        time
      }) => time > 0 && time < this.duration);
      if (!(points !== null && points !== void 0 && points.length)) return;
      const containerFragment = document.createDocumentFragment();
      const pointsFragment = document.createDocumentFragment();
      let tipElement = null;
      const tipVisible = `${this.config.classNames.tooltip}--visible`;
      const toggleTip = show => toggleClass(tipElement, tipVisible, show);

      // Inject markers to progress container
      points.forEach(point => {
        const markerElement = createElement('span', {
          class: this.config.classNames.marker
        }, '');
        const left = `${point.time / this.duration * 100}%`;
        if (tipElement) {
          // Show on hover
          markerElement.addEventListener('mouseenter', () => {
            if (point.label) return;
            tipElement.style.left = left;
            tipElement.innerHTML = point.label;
            toggleTip(true);
          });

          // Hide on leave
          markerElement.addEventListener('mouseleave', () => {
            toggleTip(false);
          });
        }
        markerElement.addEventListener('click', () => {
          this.currentTime = point.time;
        });
        markerElement.style.left = left;
        pointsFragment.appendChild(markerElement);
      });
      containerFragment.appendChild(pointsFragment);

      // Inject a tooltip if needed
      if (!this.config.tooltips.seek) {
        tipElement = createElement('span', {
          class: this.config.classNames.tooltip
        }, '');
        containerFragment.appendChild(tipElement);
      }
      this.elements.markers = {
        points: pointsFragment,
        tip: tipElement
      };
      this.elements.progress.appendChild(containerFragment);
    }
  };

  // ==========================================================================

  /**
   * Parse a string to a URL object
   * @param {String} input - the URL to be parsed
   * @param {Boolean} safe - failsafe parsing
   */
  function parseUrl(input, safe = true) {
    let url = input;
    if (safe) {
      const parser = document.createElement('a');
      parser.href = url;
      url = parser.href;
    }
    try {
      return new URL(url);
    } catch (_) {
      return null;
    }
  }

  // Convert object to URLSearchParams
  function buildUrlParams(input) {
    const params = new URLSearchParams();
    if (is.object(input)) {
      Object.entries(input).forEach(([key, value]) => {
        params.set(key, value);
      });
    }
    return params;
  }

  // ==========================================================================
  const captions = {
    // Setup captions
    setup() {
      // Requires UI support
      if (!this.supported.ui) {
        return;
      }

      // Only Vimeo and HTML5 video supported at this point
      if (!this.isVideo || this.isYouTube || this.isHTML5 && !support.textTracks) {
        // Clear menu and hide
        if (is.array(this.config.controls) && this.config.controls.includes('settings') && this.config.settings.includes('captions')) {
          controls.setCaptionsMenu.call(this);
        }
        return;
      }

      // Inject the container
      if (!is.element(this.elements.captions)) {
        this.elements.captions = createElement('div', getAttributesFromSelector(this.config.selectors.captions));
        this.elements.captions.setAttribute('dir', 'auto');
        insertAfter(this.elements.captions, this.elements.wrapper);
      }

      // Fix IE captions if CORS is used
      // Fetch captions and inject as blobs instead (data URIs not supported!)
      if (browser.isIE && window.URL) {
        const elements = this.media.querySelectorAll('track');
        Array.from(elements).forEach(track => {
          const src = track.getAttribute('src');
          const url = parseUrl(src);
          if (url !== null && url.hostname !== window.location.href.hostname && ['http:', 'https:'].includes(url.protocol)) {
            fetch(src, 'blob').then(blob => {
              track.setAttribute('src', window.URL.createObjectURL(blob));
            }).catch(() => {
              removeElement(track);
            });
          }
        });
      }

      // Get and set initial data
      // The "preferred" options are not realized unless / until the wanted language has a match
      // * languages: Array of user's browser languages.
      // * language:  The language preferred by user settings or config
      // * active:    The state preferred by user settings or config
      // * toggled:   The real captions state

      const browserLanguages = navigator.languages || [navigator.language || navigator.userLanguage || 'en'];
      const languages = dedupe(browserLanguages.map(language => language.split('-')[0]));
      let language = (this.storage.get('language') || this.config.captions.language || 'auto').toLowerCase();

      // Use first browser language when language is 'auto'
      if (language === 'auto') {
        [language] = languages;
      }
      let active = this.storage.get('captions');
      if (!is.boolean(active)) {
        ({
          active
        } = this.config.captions);
      }
      Object.assign(this.captions, {
        toggled: false,
        active,
        language,
        languages
      });

      // Watch changes to textTracks and update captions menu
      if (this.isHTML5) {
        const trackEvents = this.config.captions.update ? 'addtrack removetrack' : 'removetrack';
        on.call(this, this.media.textTracks, trackEvents, captions.update.bind(this));
      }

      // Update available languages in list next tick (the event must not be triggered before the listeners)
      setTimeout(captions.update.bind(this), 0);
    },
    // Update available language options in settings based on tracks
    update() {
      const tracks = captions.getTracks.call(this, true);
      // Get the wanted language
      const {
        active,
        language,
        meta,
        currentTrackNode
      } = this.captions;
      const languageExists = Boolean(tracks.find(track => track.language === language));

      // Handle tracks (add event listener and "pseudo"-default)
      if (this.isHTML5 && this.isVideo) {
        tracks.filter(track => !meta.get(track)).forEach(track => {
          this.debug.log('Track added', track);

          // Attempt to store if the original dom element was "default"
          meta.set(track, {
            default: track.mode === 'showing'
          });

          // Turn off native caption rendering to avoid double captions
          // Note: mode='hidden' forces a track to download. To ensure every track
          // isn't downloaded at once, only 'showing' tracks should be reassigned
          // eslint-disable-next-line no-param-reassign
          if (track.mode === 'showing') {
            // eslint-disable-next-line no-param-reassign
            track.mode = 'hidden';
          }

          // Add event listener for cue changes
          on.call(this, track, 'cuechange', () => captions.updateCues.call(this));
        });
      }

      // Update language first time it matches, or if the previous matching track was removed
      if (languageExists && this.language !== language || !tracks.includes(currentTrackNode)) {
        captions.setLanguage.call(this, language);
        captions.toggle.call(this, active && languageExists);
      }

      // Enable or disable captions based on track length
      if (this.elements) {
        toggleClass(this.elements.container, this.config.classNames.captions.enabled, !is.empty(tracks));
      }

      // Update available languages in list
      if (is.array(this.config.controls) && this.config.controls.includes('settings') && this.config.settings.includes('captions')) {
        controls.setCaptionsMenu.call(this);
      }
    },
    // Toggle captions display
    // Used internally for the toggleCaptions method, with the passive option forced to false
    toggle(input, passive = true) {
      // If there's no full support
      if (!this.supported.ui) {
        return;
      }
      const {
        toggled
      } = this.captions; // Current state
      const activeClass = this.config.classNames.captions.active;
      // Get the next state
      // If the method is called without parameter, toggle based on current value
      const active = is.nullOrUndefined(input) ? !toggled : input;

      // Update state and trigger event
      if (active !== toggled) {
        // When passive, don't override user preferences
        if (!passive) {
          this.captions.active = active;
          this.storage.set({
            captions: active
          });
        }

        // Force language if the call isn't passive and there is no matching language to toggle to
        if (!this.language && active && !passive) {
          const tracks = captions.getTracks.call(this);
          const track = captions.findTrack.call(this, [this.captions.language, ...this.captions.languages], true);

          // Override user preferences to avoid switching languages if a matching track is added
          this.captions.language = track.language;

          // Set caption, but don't store in localStorage as user preference
          captions.set.call(this, tracks.indexOf(track));
          return;
        }

        // Toggle button if it's enabled
        if (this.elements.buttons.captions) {
          this.elements.buttons.captions.pressed = active;
        }

        // Add class hook
        toggleClass(this.elements.container, activeClass, active);
        this.captions.toggled = active;

        // Update settings menu
        controls.updateSetting.call(this, 'captions');

        // Trigger event (not used internally)
        triggerEvent.call(this, this.media, active ? 'captionsenabled' : 'captionsdisabled');
      }

      // Wait for the call stack to clear before setting mode='hidden'
      // on the active track - forcing the browser to download it
      setTimeout(() => {
        if (active && this.captions.toggled) {
          this.captions.currentTrackNode.mode = 'hidden';
        }
      });
    },
    // Set captions by track index
    // Used internally for the currentTrack setter with the passive option forced to false
    set(index, passive = true) {
      const tracks = captions.getTracks.call(this);

      // Disable captions if setting to -1
      if (index === -1) {
        captions.toggle.call(this, false, passive);
        return;
      }
      if (!is.number(index)) {
        this.debug.warn('Invalid caption argument', index);
        return;
      }
      if (!(index in tracks)) {
        this.debug.warn('Track not found', index);
        return;
      }
      if (this.captions.currentTrack !== index) {
        this.captions.currentTrack = index;
        const track = tracks[index];
        const {
          language
        } = track || {};

        // Store reference to node for invalidation on remove
        this.captions.currentTrackNode = track;

        // Update settings menu
        controls.updateSetting.call(this, 'captions');

        // When passive, don't override user preferences
        if (!passive) {
          this.captions.language = language;
          this.storage.set({
            language
          });
        }

        // Handle Vimeo captions
        if (this.isVimeo) {
          this.embed.enableTextTrack(language);
        }

        // Trigger event
        triggerEvent.call(this, this.media, 'languagechange');
      }

      // Show captions
      captions.toggle.call(this, true, passive);
      if (this.isHTML5 && this.isVideo) {
        // If we change the active track while a cue is already displayed we need to update it
        captions.updateCues.call(this);
      }
    },
    // Set captions by language
    // Used internally for the language setter with the passive option forced to false
    setLanguage(input, passive = true) {
      if (!is.string(input)) {
        this.debug.warn('Invalid language argument', input);
        return;
      }
      // Normalize
      const language = input.toLowerCase();
      this.captions.language = language;

      // Set currentTrack
      const tracks = captions.getTracks.call(this);
      const track = captions.findTrack.call(this, [language]);
      captions.set.call(this, tracks.indexOf(track), passive);
    },
    // Get current valid caption tracks
    // If update is false it will also ignore tracks without metadata
    // This is used to "freeze" the language options when captions.update is false
    getTracks(update = false) {
      // Handle media or textTracks missing or null
      const tracks = Array.from((this.media || {}).textTracks || []);
      // For HTML5, use cache instead of current tracks when it exists (if captions.update is false)
      // Filter out removed tracks and tracks that aren't captions/subtitles (for example metadata)
      return tracks.filter(track => !this.isHTML5 || update || this.captions.meta.has(track)).filter(track => ['captions', 'subtitles'].includes(track.kind));
    },
    // Match tracks based on languages and get the first
    findTrack(languages, force = false) {
      const tracks = captions.getTracks.call(this);
      const sortIsDefault = track => Number((this.captions.meta.get(track) || {}).default);
      const sorted = Array.from(tracks).sort((a, b) => sortIsDefault(b) - sortIsDefault(a));
      let track;
      languages.every(language => {
        track = sorted.find(t => t.language === language);
        return !track; // Break iteration if there is a match
      });

      // If no match is found but is required, get first
      return track || (force ? sorted[0] : undefined);
    },
    // Get the current track
    getCurrentTrack() {
      return captions.getTracks.call(this)[this.currentTrack];
    },
    // Get UI label for track
    getLabel(track) {
      let currentTrack = track;
      if (!is.track(currentTrack) && support.textTracks && this.captions.toggled) {
        currentTrack = captions.getCurrentTrack.call(this);
      }
      if (is.track(currentTrack)) {
        if (!is.empty(currentTrack.label)) {
          return currentTrack.label;
        }
        if (!is.empty(currentTrack.language)) {
          return track.language.toUpperCase();
        }
        return i18n.get('enabled', this.config);
      }
      return i18n.get('disabled', this.config);
    },
    // Update captions using current track's active cues
    // Also optional array argument in case there isn't any track (ex: vimeo)
    updateCues(input) {
      // Requires UI
      if (!this.supported.ui) {
        return;
      }
      if (!is.element(this.elements.captions)) {
        this.debug.warn('No captions element to render to');
        return;
      }

      // Only accept array or empty input
      if (!is.nullOrUndefined(input) && !Array.isArray(input)) {
        this.debug.warn('updateCues: Invalid input', input);
        return;
      }
      let cues = input;

      // Get cues from track
      if (!cues) {
        const track = captions.getCurrentTrack.call(this);
        cues = Array.from((track || {}).activeCues || []).map(cue => cue.getCueAsHTML()).map(getHTML);
      }

      // Set new caption text
      const content = cues.map(cueText => cueText.trim()).join('\n');
      const changed = content !== this.elements.captions.innerHTML;
      if (changed) {
        // Empty the container and create a new child element
        emptyElement(this.elements.captions);
        const caption = createElement('span', getAttributesFromSelector(this.config.selectors.caption));
        caption.innerHTML = content;
        this.elements.captions.appendChild(caption);

        // Trigger event
        triggerEvent.call(this, this.media, 'cuechange');
      }
    }
  };

  // ==========================================================================
  // Plyr default config
  // ==========================================================================

  const defaults = {
    // Disable
    enabled: true,
    // Custom media title
    title: '',
    // Logging to console
    debug: false,
    // Auto play (if supported)
    autoplay: false,
    // Only allow one media playing at once (vimeo only)
    autopause: true,
    // Allow inline playback on iOS
    playsinline: true,
    // Default time to skip when rewind/fast forward
    seekTime: 10,
    // Default volume
    volume: 1,
    muted: false,
    // Pass a custom duration
    duration: null,
    // Display the media duration on load in the current time position
    // If you have opted to display both duration and currentTime, this is ignored
    displayDuration: true,
    // Invert the current time to be a countdown
    invertTime: true,
    // Clicking the currentTime inverts it's value to show time left rather than elapsed
    toggleInvert: true,
    // Force an aspect ratio
    // The format must be `'w:h'` (e.g. `'16:9'`)
    ratio: null,
    // Click video container to play/pause
    clickToPlay: true,
    // Auto hide the controls
    hideControls: true,
    // Reset to start when playback ended
    resetOnEnd: false,
    // Disable the standard context menu
    disableContextMenu: true,
    // Sprite (for icons)
    loadSprite: true,
    iconPrefix: 'plyr',
    iconUrl: 'https://cdn.plyr.io/3.7.8/plyr.svg',
    // Blank video (used to prevent errors on source change)
    blankVideo: 'https://cdn.plyr.io/static/blank.mp4',
    // Quality default
    quality: {
      default: 576,
      // The options to display in the UI, if available for the source media
      options: [4320, 2880, 2160, 1440, 1080, 720, 576, 480, 360, 240],
      forced: false,
      onChange: null
    },
    // Set loops
    loop: {
      active: false
      // start: null,
      // end: null,
    },

    // Speed default and options to display
    speed: {
      selected: 1,
      // The options to display in the UI, if available for the source media (e.g. Vimeo and YouTube only support 0.5x-4x)
      options: [0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 4]
    },
    // Keyboard shortcut settings
    keyboard: {
      focused: true,
      global: false
    },
    // Display tooltips
    tooltips: {
      controls: false,
      seek: true
    },
    // Captions settings
    captions: {
      active: false,
      language: 'auto',
      // Listen to new tracks added after Plyr is initialized.
      // This is needed for streaming captions, but may result in unselectable options
      update: false
    },
    // Fullscreen settings
    fullscreen: {
      enabled: true,
      // Allow fullscreen?
      fallback: true,
      // Fallback using full viewport/window
      iosNative: false // Use the native fullscreen in iOS (disables custom controls)
      // Selector for the fullscreen container so contextual / non-player content can remain visible in fullscreen mode
      // Non-ancestors of the player element will be ignored
      // container: null, // defaults to the player element
    },

    // Local storage
    storage: {
      enabled: true,
      key: 'plyr'
    },
    // Default controls
    controls: ['play-large',
    // 'restart',
    // 'rewind',
    'play',
    // 'fast-forward',
    'progress', 'current-time',
    // 'duration',
    'mute', 'volume', 'captions', 'settings', 'pip', 'airplay',
    // 'download',
    'fullscreen'],
    settings: ['captions', 'quality', 'speed'],
    // Localisation
    i18n: {
      restart: 'Restart',
      rewind: 'Rewind {seektime}s',
      play: 'Play',
      pause: 'Pause',
      fastForward: 'Forward {seektime}s',
      seek: 'Seek',
      seekLabel: '{currentTime} of {duration}',
      played: 'Played',
      buffered: 'Buffered',
      currentTime: 'Current time',
      duration: 'Duration',
      volume: 'Volume',
      mute: 'Mute',
      unmute: 'Unmute',
      enableCaptions: 'Enable captions',
      disableCaptions: 'Disable captions',
      download: 'Download',
      enterFullscreen: 'Enter fullscreen',
      exitFullscreen: 'Exit fullscreen',
      frameTitle: 'Player for {title}',
      captions: 'Captions',
      settings: 'Settings',
      pip: 'PIP',
      menuBack: 'Go back to previous menu',
      speed: 'Speed',
      normal: 'Normal',
      quality: 'Quality',
      loop: 'Loop',
      start: 'Start',
      end: 'End',
      all: 'All',
      reset: 'Reset',
      disabled: 'Disabled',
      enabled: 'Enabled',
      advertisement: 'Ad',
      qualityBadge: {
        2160: '4K',
        1440: 'HD',
        1080: 'HD',
        720: 'HD',
        576: 'SD',
        480: 'SD'
      }
    },
    // URLs
    urls: {
      download: null,
      vimeo: {
        sdk: 'https://player.vimeo.com/api/player.js',
        iframe: 'https://player.vimeo.com/video/{0}?{1}',
        api: 'https://vimeo.com/api/oembed.json?url={0}'
      },
      youtube: {
        sdk: 'https://www.youtube.com/iframe_api',
        api: 'https://noembed.com/embed?url=https://www.youtube.com/watch?v={0}'
      },
      googleIMA: {
        sdk: 'https://imasdk.googleapis.com/js/sdkloader/ima3.js'
      }
    },
    // Custom control listeners
    listeners: {
      seek: null,
      play: null,
      pause: null,
      restart: null,
      rewind: null,
      fastForward: null,
      mute: null,
      volume: null,
      captions: null,
      download: null,
      fullscreen: null,
      pip: null,
      airplay: null,
      speed: null,
      quality: null,
      loop: null,
      language: null
    },
    // Events to watch and bubble
    events: [
    // Events to watch on HTML5 media elements and bubble
    // https://developer.mozilla.org/en/docs/Web/Guide/Events/Media_events
    'ended', 'progress', 'stalled', 'playing', 'waiting', 'canplay', 'canplaythrough', 'loadstart', 'loadeddata', 'loadedmetadata', 'timeupdate', 'volumechange', 'play', 'pause', 'error', 'seeking', 'seeked', 'emptied', 'ratechange', 'cuechange',
    // Custom events
    'download', 'enterfullscreen', 'exitfullscreen', 'captionsenabled', 'captionsdisabled', 'languagechange', 'controlshidden', 'controlsshown', 'ready',
    // YouTube
    'statechange',
    // Quality
    'qualitychange',
    // Ads
    'adsloaded', 'adscontentpause', 'adscontentresume', 'adstarted', 'adsmidpoint', 'adscomplete', 'adsallcomplete', 'adsimpression', 'adsclick'],
    // Selectors
    // Change these to match your template if using custom HTML
    selectors: {
      editable: 'input, textarea, select, [contenteditable]',
      container: '.plyr',
      controls: {
        container: null,
        wrapper: '.plyr__controls'
      },
      labels: '[data-plyr]',
      buttons: {
        play: '[data-plyr="play"]',
        pause: '[data-plyr="pause"]',
        restart: '[data-plyr="restart"]',
        rewind: '[data-plyr="rewind"]',
        fastForward: '[data-plyr="fast-forward"]',
        mute: '[data-plyr="mute"]',
        captions: '[data-plyr="captions"]',
        download: '[data-plyr="download"]',
        fullscreen: '[data-plyr="fullscreen"]',
        pip: '[data-plyr="pip"]',
        airplay: '[data-plyr="airplay"]',
        settings: '[data-plyr="settings"]',
        loop: '[data-plyr="loop"]'
      },
      inputs: {
        seek: '[data-plyr="seek"]',
        volume: '[data-plyr="volume"]',
        speed: '[data-plyr="speed"]',
        language: '[data-plyr="language"]',
        quality: '[data-plyr="quality"]'
      },
      display: {
        currentTime: '.plyr__time--current',
        duration: '.plyr__time--duration',
        buffer: '.plyr__progress__buffer',
        loop: '.plyr__progress__loop',
        // Used later
        volume: '.plyr__volume--display'
      },
      progress: '.plyr__progress',
      captions: '.plyr__captions',
      caption: '.plyr__caption'
    },
    // Class hooks added to the player in different states
    classNames: {
      type: 'plyr--{0}',
      provider: 'plyr--{0}',
      video: 'plyr__video-wrapper',
      embed: 'plyr__video-embed',
      videoFixedRatio: 'plyr__video-wrapper--fixed-ratio',
      embedContainer: 'plyr__video-embed__container',
      poster: 'plyr__poster',
      posterEnabled: 'plyr__poster-enabled',
      ads: 'plyr__ads',
      control: 'plyr__control',
      controlPressed: 'plyr__control--pressed',
      playing: 'plyr--playing',
      paused: 'plyr--paused',
      stopped: 'plyr--stopped',
      loading: 'plyr--loading',
      hover: 'plyr--hover',
      tooltip: 'plyr__tooltip',
      cues: 'plyr__cues',
      marker: 'plyr__progress__marker',
      hidden: 'plyr__sr-only',
      hideControls: 'plyr--hide-controls',
      isTouch: 'plyr--is-touch',
      uiSupported: 'plyr--full-ui',
      noTransition: 'plyr--no-transition',
      display: {
        time: 'plyr__time'
      },
      menu: {
        value: 'plyr__menu__value',
        badge: 'plyr__badge',
        open: 'plyr--menu-open'
      },
      captions: {
        enabled: 'plyr--captions-enabled',
        active: 'plyr--captions-active'
      },
      fullscreen: {
        enabled: 'plyr--fullscreen-enabled',
        fallback: 'plyr--fullscreen-fallback'
      },
      pip: {
        supported: 'plyr--pip-supported',
        active: 'plyr--pip-active'
      },
      airplay: {
        supported: 'plyr--airplay-supported',
        active: 'plyr--airplay-active'
      },
      previewThumbnails: {
        // Tooltip thumbs
        thumbContainer: 'plyr__preview-thumb',
        thumbContainerShown: 'plyr__preview-thumb--is-shown',
        imageContainer: 'plyr__preview-thumb__image-container',
        timeContainer: 'plyr__preview-thumb__time-container',
        // Scrubbing
        scrubbingContainer: 'plyr__preview-scrubbing',
        scrubbingContainerShown: 'plyr__preview-scrubbing--is-shown'
      }
    },
    // Embed attributes
    attributes: {
      embed: {
        provider: 'data-plyr-provider',
        id: 'data-plyr-embed-id',
        hash: 'data-plyr-embed-hash'
      }
    },
    // Advertisements plugin
    // Register for an account here: http://vi.ai/publisher-video-monetization/?aid=plyrio
    ads: {
      enabled: false,
      publisherId: '',
      tagUrl: ''
    },
    // Preview Thumbnails plugin
    previewThumbnails: {
      enabled: false,
      src: ''
    },
    // Vimeo plugin
    vimeo: {
      byline: false,
      portrait: false,
      title: false,
      speed: true,
      transparent: false,
      // Custom settings from Plyr
      customControls: true,
      referrerPolicy: null,
      // https://developer.mozilla.org/en-US/docs/Web/API/HTMLIFrameElement/referrerPolicy
      // Whether the owner of the video has a Pro or Business account
      // (which allows us to properly hide controls without CSS hacks, etc)
      premium: false
    },
    // YouTube plugin
    youtube: {
      rel: 0,
      // No related vids
      showinfo: 0,
      // Hide info
      iv_load_policy: 3,
      // Hide annotations
      modestbranding: 1,
      // Hide logos as much as possible (they still show one in the corner when paused)
      // Custom settings from Plyr
      customControls: true,
      noCookie: false // Whether to use an alternative version of YouTube without cookies
    },

    // Media Metadata
    mediaMetadata: {
      title: '',
      artist: '',
      album: '',
      artwork: []
    },
    // Markers
    markers: {
      enabled: false,
      points: []
    }
  };

  // ==========================================================================
  // Plyr states
  // ==========================================================================

  const pip = {
    active: 'picture-in-picture',
    inactive: 'inline'
  };

  // ==========================================================================
  // Plyr supported types and providers
  // ==========================================================================

  const providers = {
    html5: 'html5',
    youtube: 'youtube',
    vimeo: 'vimeo'
  };
  const types = {
    audio: 'audio',
    video: 'video'
  };

  /**
   * Get provider by URL
   * @param {String} url
   */
  function getProviderByUrl(url) {
    // YouTube
    if (/^(https?:\/\/)?(www\.)?(youtube\.com|youtube-nocookie\.com|youtu\.?be)\/.+$/.test(url)) {
      return providers.youtube;
    }

    // Vimeo
    if (/^https?:\/\/player.vimeo.com\/video\/\d{0,9}(?=\b|\/)/.test(url)) {
      return providers.vimeo;
    }
    return null;
  }

  // ==========================================================================
  // Console wrapper
  // ==========================================================================

  const noop = () => {};
  class Console {
    constructor(enabled = false) {
      this.enabled = window.console && enabled;
      if (this.enabled) {
        this.log('Debugging enabled');
      }
    }
    get log() {
      // eslint-disable-next-line no-console
      return this.enabled ? Function.prototype.bind.call(console.log, console) : noop;
    }
    get warn() {
      // eslint-disable-next-line no-console
      return this.enabled ? Function.prototype.bind.call(console.warn, console) : noop;
    }
    get error() {
      // eslint-disable-next-line no-console
      return this.enabled ? Function.prototype.bind.call(console.error, console) : noop;
    }
  }

  class Fullscreen {
    constructor(player) {
      _defineProperty$1(this, "onChange", () => {
        if (!this.supported) return;

        // Update toggle button
        const button = this.player.elements.buttons.fullscreen;
        if (is.element(button)) {
          button.pressed = this.active;
        }

        // Always trigger events on the plyr / media element (not a fullscreen container) and let them bubble up
        const target = this.target === this.player.media ? this.target : this.player.elements.container;
        // Trigger an event
        triggerEvent.call(this.player, target, this.active ? 'enterfullscreen' : 'exitfullscreen', true);
      });
      _defineProperty$1(this, "toggleFallback", (toggle = false) => {
        // Store or restore scroll position
        if (toggle) {
          this.scrollPosition = {
            x: window.scrollX ?? 0,
            y: window.scrollY ?? 0
          };
        } else {
          window.scrollTo(this.scrollPosition.x, this.scrollPosition.y);
        }

        // Toggle scroll
        document.body.style.overflow = toggle ? 'hidden' : '';

        // Toggle class hook
        toggleClass(this.target, this.player.config.classNames.fullscreen.fallback, toggle);

        // Force full viewport on iPhone X+
        if (browser.isIos) {
          let viewport = document.head.querySelector('meta[name="viewport"]');
          const property = 'viewport-fit=cover';

          // Inject the viewport meta if required
          if (!viewport) {
            viewport = document.createElement('meta');
            viewport.setAttribute('name', 'viewport');
          }

          // Check if the property already exists
          const hasProperty = is.string(viewport.content) && viewport.content.includes(property);
          if (toggle) {
            this.cleanupViewport = !hasProperty;
            if (!hasProperty) viewport.content += `,${property}`;
          } else if (this.cleanupViewport) {
            viewport.content = viewport.content.split(',').filter(part => part.trim() !== property).join(',');
          }
        }

        // Toggle button and fire events
        this.onChange();
      });
      // Trap focus inside container
      _defineProperty$1(this, "trapFocus", event => {
        // Bail if iOS/iPadOS, not active, not the tab key
        if (browser.isIos || browser.isIPadOS || !this.active || event.key !== 'Tab') return;

        // Get the current focused element
        const focused = document.activeElement;
        const focusable = getElements.call(this.player, 'a[href], button:not(:disabled), input:not(:disabled), [tabindex]');
        const [first] = focusable;
        const last = focusable[focusable.length - 1];
        if (focused === last && !event.shiftKey) {
          // Move focus to first element that can be tabbed if Shift isn't used
          first.focus();
          event.preventDefault();
        } else if (focused === first && event.shiftKey) {
          // Move focus to last element that can be tabbed if Shift is used
          last.focus();
          event.preventDefault();
        }
      });
      // Update UI
      _defineProperty$1(this, "update", () => {
        if (this.supported) {
          let mode;
          if (this.forceFallback) mode = 'Fallback (forced)';else if (Fullscreen.nativeSupported) mode = 'Native';else mode = 'Fallback';
          this.player.debug.log(`${mode} fullscreen enabled`);
        } else {
          this.player.debug.log('Fullscreen not supported and fallback disabled');
        }

        // Add styling hook to show button
        toggleClass(this.player.elements.container, this.player.config.classNames.fullscreen.enabled, this.supported);
      });
      // Make an element fullscreen
      _defineProperty$1(this, "enter", () => {
        if (!this.supported) return;

        // iOS native fullscreen doesn't need the request step
        if (browser.isIos && this.player.config.fullscreen.iosNative) {
          if (this.player.isVimeo) {
            this.player.embed.requestFullscreen();
          } else {
            this.target.webkitEnterFullscreen();
          }
        } else if (!Fullscreen.nativeSupported || this.forceFallback) {
          this.toggleFallback(true);
        } else if (!this.prefix) {
          this.target.requestFullscreen({
            navigationUI: 'hide'
          });
        } else if (!is.empty(this.prefix)) {
          this.target[`${this.prefix}Request${this.property}`]();
        }
      });
      // Bail from fullscreen
      _defineProperty$1(this, "exit", () => {
        if (!this.supported) return;

        // iOS native fullscreen
        if (browser.isIos && this.player.config.fullscreen.iosNative) {
          if (this.player.isVimeo) {
            this.player.embed.exitFullscreen();
          } else {
            this.target.webkitEnterFullscreen();
          }
          silencePromise(this.player.play());
        } else if (!Fullscreen.nativeSupported || this.forceFallback) {
          this.toggleFallback(false);
        } else if (!this.prefix) {
          (document.cancelFullScreen || document.exitFullscreen).call(document);
        } else if (!is.empty(this.prefix)) {
          const action = this.prefix === 'moz' ? 'Cancel' : 'Exit';
          document[`${this.prefix}${action}${this.property}`]();
        }
      });
      // Toggle state
      _defineProperty$1(this, "toggle", () => {
        if (!this.active) this.enter();else this.exit();
      });
      // Keep reference to parent
      this.player = player;

      // Get prefix
      this.prefix = Fullscreen.prefix;
      this.property = Fullscreen.property;

      // Scroll position
      this.scrollPosition = {
        x: 0,
        y: 0
      };

      // Force the use of 'full window/browser' rather than fullscreen
      this.forceFallback = player.config.fullscreen.fallback === 'force';

      // Get the fullscreen element
      // Checks container is an ancestor, defaults to null
      this.player.elements.fullscreen = player.config.fullscreen.container && closest$1(this.player.elements.container, player.config.fullscreen.container);

      // Register event listeners
      // Handle event (incase user presses escape etc)
      on.call(this.player, document, this.prefix === 'ms' ? 'MSFullscreenChange' : `${this.prefix}fullscreenchange`, () => {
        // TODO: Filter for target??
        this.onChange();
      });

      // Fullscreen toggle on double click
      on.call(this.player, this.player.elements.container, 'dblclick', event => {
        // Ignore double click in controls
        if (is.element(this.player.elements.controls) && this.player.elements.controls.contains(event.target)) {
          return;
        }
        this.player.listeners.proxy(event, this.toggle, 'fullscreen');
      });

      // Tap focus when in fullscreen
      on.call(this, this.player.elements.container, 'keydown', event => this.trapFocus(event));

      // Update the UI
      this.update();
    }

    // Determine if native supported
    static get nativeSupported() {
      return !!(document.fullscreenEnabled || document.webkitFullscreenEnabled || document.mozFullScreenEnabled || document.msFullscreenEnabled);
    }

    // If we're actually using native
    get useNative() {
      return Fullscreen.nativeSupported && !this.forceFallback;
    }

    // Get the prefix for handlers
    static get prefix() {
      // No prefix
      if (is.function(document.exitFullscreen)) return '';

      // Check for fullscreen support by vendor prefix
      let value = '';
      const prefixes = ['webkit', 'moz', 'ms'];
      prefixes.some(pre => {
        if (is.function(document[`${pre}ExitFullscreen`]) || is.function(document[`${pre}CancelFullScreen`])) {
          value = pre;
          return true;
        }
        return false;
      });
      return value;
    }
    static get property() {
      return this.prefix === 'moz' ? 'FullScreen' : 'Fullscreen';
    }

    // Determine if fullscreen is supported
    get supported() {
      return [
      // Fullscreen is enabled in config
      this.player.config.fullscreen.enabled,
      // Must be a video
      this.player.isVideo,
      // Either native is supported or fallback enabled
      Fullscreen.nativeSupported || this.player.config.fullscreen.fallback,
      // YouTube has no way to trigger fullscreen, so on devices with no native support, playsinline
      // must be enabled and iosNative fullscreen must be disabled to offer the fullscreen fallback
      !this.player.isYouTube || Fullscreen.nativeSupported || !browser.isIos || this.player.config.playsinline && !this.player.config.fullscreen.iosNative].every(Boolean);
    }

    // Get active state
    get active() {
      if (!this.supported) return false;

      // Fallback using classname
      if (!Fullscreen.nativeSupported || this.forceFallback) {
        return hasClass(this.target, this.player.config.classNames.fullscreen.fallback);
      }
      const element = !this.prefix ? this.target.getRootNode().fullscreenElement : this.target.getRootNode()[`${this.prefix}${this.property}Element`];
      return element && element.shadowRoot ? element === this.target.getRootNode().host : element === this.target;
    }

    // Get target element
    get target() {
      return browser.isIos && this.player.config.fullscreen.iosNative ? this.player.media : this.player.elements.fullscreen ?? this.player.elements.container;
    }
  }

  // ==========================================================================
  // Load image avoiding xhr/fetch CORS issues
  // Server status can't be obtained this way unfortunately, so this uses "naturalWidth" to determine if the image has loaded
  // By default it checks if it is at least 1px, but you can add a second argument to change this
  // ==========================================================================

  function loadImage(src, minWidth = 1) {
    return new Promise((resolve, reject) => {
      const image = new Image();
      const handler = () => {
        delete image.onload;
        delete image.onerror;
        (image.naturalWidth >= minWidth ? resolve : reject)(image);
      };
      Object.assign(image, {
        onload: handler,
        onerror: handler,
        src
      });
    });
  }

  // ==========================================================================
  const ui = {
    addStyleHook() {
      toggleClass(this.elements.container, this.config.selectors.container.replace('.', ''), true);
      toggleClass(this.elements.container, this.config.classNames.uiSupported, this.supported.ui);
    },
    // Toggle native HTML5 media controls
    toggleNativeControls(toggle = false) {
      if (toggle && this.isHTML5) {
        this.media.setAttribute('controls', '');
      } else {
        this.media.removeAttribute('controls');
      }
    },
    // Setup the UI
    build() {
      // Re-attach media element listeners
      // TODO: Use event bubbling?
      this.listeners.media();

      // Don't setup interface if no support
      if (!this.supported.ui) {
        this.debug.warn(`Basic support only for ${this.provider} ${this.type}`);

        // Restore native controls
        ui.toggleNativeControls.call(this, true);

        // Bail
        return;
      }

      // Inject custom controls if not present
      if (!is.element(this.elements.controls)) {
        // Inject custom controls
        controls.inject.call(this);

        // Re-attach control listeners
        this.listeners.controls();
      }

      // Remove native controls
      ui.toggleNativeControls.call(this);

      // Setup captions for HTML5
      if (this.isHTML5) {
        captions.setup.call(this);
      }

      // Reset volume
      this.volume = null;

      // Reset mute state
      this.muted = null;

      // Reset loop state
      this.loop = null;

      // Reset quality setting
      this.quality = null;

      // Reset speed
      this.speed = null;

      // Reset volume display
      controls.updateVolume.call(this);

      // Reset time display
      controls.timeUpdate.call(this);

      // Reset duration display
      controls.durationUpdate.call(this);

      // Update the UI
      ui.checkPlaying.call(this);

      // Check for picture-in-picture support
      toggleClass(this.elements.container, this.config.classNames.pip.supported, support.pip && this.isHTML5 && this.isVideo);

      // Check for airplay support
      toggleClass(this.elements.container, this.config.classNames.airplay.supported, support.airplay && this.isHTML5);

      // Add touch class
      toggleClass(this.elements.container, this.config.classNames.isTouch, this.touch);

      // Ready for API calls
      this.ready = true;

      // Ready event at end of execution stack
      setTimeout(() => {
        triggerEvent.call(this, this.media, 'ready');
      }, 0);

      // Set the title
      ui.setTitle.call(this);

      // Assure the poster image is set, if the property was added before the element was created
      if (this.poster) {
        ui.setPoster.call(this, this.poster, false).catch(() => {});
      }

      // Manually set the duration if user has overridden it.
      // The event listeners for it doesn't get called if preload is disabled (#701)
      if (this.config.duration) {
        controls.durationUpdate.call(this);
      }

      // Media metadata
      if (this.config.mediaMetadata) {
        controls.setMediaMetadata.call(this);
      }
    },
    // Setup aria attribute for play and iframe title
    setTitle() {
      // Find the current text
      let label = i18n.get('play', this.config);

      // If there's a media title set, use that for the label
      if (is.string(this.config.title) && !is.empty(this.config.title)) {
        label += `, ${this.config.title}`;
      }

      // If there's a play button, set label
      Array.from(this.elements.buttons.play || []).forEach(button => {
        button.setAttribute('aria-label', label);
      });

      // Set iframe title
      // https://github.com/sampotts/plyr/issues/124
      if (this.isEmbed) {
        const iframe = getElement.call(this, 'iframe');
        if (!is.element(iframe)) {
          return;
        }

        // Default to media type
        const title = !is.empty(this.config.title) ? this.config.title : 'video';
        const format = i18n.get('frameTitle', this.config);
        iframe.setAttribute('title', format.replace('{title}', title));
      }
    },
    // Toggle poster
    togglePoster(enable) {
      toggleClass(this.elements.container, this.config.classNames.posterEnabled, enable);
    },
    // Set the poster image (async)
    // Used internally for the poster setter, with the passive option forced to false
    setPoster(poster, passive = true) {
      // Don't override if call is passive
      if (passive && this.poster) {
        return Promise.reject(new Error('Poster already set'));
      }

      // Set property synchronously to respect the call order
      this.media.setAttribute('data-poster', poster);

      // Show the poster
      this.elements.poster.removeAttribute('hidden');

      // Wait until ui is ready
      return ready.call(this)
      // Load image
      .then(() => loadImage(poster)).catch(error => {
        // Hide poster on error unless it's been set by another call
        if (poster === this.poster) {
          ui.togglePoster.call(this, false);
        }
        // Rethrow
        throw error;
      }).then(() => {
        // Prevent race conditions
        if (poster !== this.poster) {
          throw new Error('setPoster cancelled by later call to setPoster');
        }
      }).then(() => {
        Object.assign(this.elements.poster.style, {
          backgroundImage: `url('${poster}')`,
          // Reset backgroundSize as well (since it can be set to "cover" for padded thumbnails for youtube)
          backgroundSize: ''
        });
        ui.togglePoster.call(this, true);
        return poster;
      });
    },
    // Check playing state
    checkPlaying(event) {
      // Class hooks
      toggleClass(this.elements.container, this.config.classNames.playing, this.playing);
      toggleClass(this.elements.container, this.config.classNames.paused, this.paused);
      toggleClass(this.elements.container, this.config.classNames.stopped, this.stopped);

      // Set state
      Array.from(this.elements.buttons.play || []).forEach(target => {
        Object.assign(target, {
          pressed: this.playing
        });
        target.setAttribute('aria-label', i18n.get(this.playing ? 'pause' : 'play', this.config));
      });

      // Only update controls on non timeupdate events
      if (is.event(event) && event.type === 'timeupdate') {
        return;
      }

      // Toggle controls
      ui.toggleControls.call(this);
    },
    // Check if media is loading
    checkLoading(event) {
      this.loading = ['stalled', 'waiting'].includes(event.type);

      // Clear timer
      clearTimeout(this.timers.loading);

      // Timer to prevent flicker when seeking
      this.timers.loading = setTimeout(() => {
        // Update progress bar loading class state
        toggleClass(this.elements.container, this.config.classNames.loading, this.loading);

        // Update controls visibility
        ui.toggleControls.call(this);
      }, this.loading ? 250 : 0);
    },
    // Toggle controls based on state and `force` argument
    toggleControls(force) {
      const {
        controls: controlsElement
      } = this.elements;
      if (controlsElement && this.config.hideControls) {
        // Don't hide controls if a touch-device user recently seeked. (Must be limited to touch devices, or it occasionally prevents desktop controls from hiding.)
        const recentTouchSeek = this.touch && this.lastSeekTime + 2000 > Date.now();

        // Show controls if force, loading, paused, button interaction, or recent seek, otherwise hide
        this.toggleControls(Boolean(force || this.loading || this.paused || controlsElement.pressed || controlsElement.hover || recentTouchSeek));
      }
    },
    // Migrate any custom properties from the media to the parent
    migrateStyles() {
      // Loop through values (as they are the keys when the object is spread 🤔)
      Object.values({
        ...this.media.style
      })
      // We're only fussed about Plyr specific properties
      .filter(key => !is.empty(key) && is.string(key) && key.startsWith('--plyr')).forEach(key => {
        // Set on the container
        this.elements.container.style.setProperty(key, this.media.style.getPropertyValue(key));

        // Clean up from media element
        this.media.style.removeProperty(key);
      });

      // Remove attribute if empty
      if (is.empty(this.media.style)) {
        this.media.removeAttribute('style');
      }
    }
  };

  class Listeners {
    constructor(_player) {
      // Device is touch enabled
      _defineProperty$1(this, "firstTouch", () => {
        const {
          player
        } = this;
        const {
          elements
        } = player;
        player.touch = true;

        // Add touch class
        toggleClass(elements.container, player.config.classNames.isTouch, true);
      });
      // Global window & document listeners
      _defineProperty$1(this, "global", (toggle = true) => {
        const {
          player
        } = this;

        // Keyboard shortcuts
        if (player.config.keyboard.global) {
          toggleListener.call(player, window, 'keydown keyup', this.handleKey, toggle, false);
        }

        // Click anywhere closes menu
        toggleListener.call(player, document.body, 'click', this.toggleMenu, toggle);

        // Detect touch by events
        once.call(player, document.body, 'touchstart', this.firstTouch);
      });
      // Container listeners
      _defineProperty$1(this, "container", () => {
        const {
          player
        } = this;
        const {
          config,
          elements,
          timers
        } = player;

        // Keyboard shortcuts
        if (!config.keyboard.global && config.keyboard.focused) {
          on.call(player, elements.container, 'keydown keyup', this.handleKey, false);
        }

        // Toggle controls on mouse events and entering fullscreen
        on.call(player, elements.container, 'mousemove mouseleave touchstart touchmove enterfullscreen exitfullscreen', event => {
          const {
            controls: controlsElement
          } = elements;

          // Remove button states for fullscreen
          if (controlsElement && event.type === 'enterfullscreen') {
            controlsElement.pressed = false;
            controlsElement.hover = false;
          }

          // Show, then hide after a timeout unless another control event occurs
          const show = ['touchstart', 'touchmove', 'mousemove'].includes(event.type);
          let delay = 0;
          if (show) {
            ui.toggleControls.call(player, true);
            // Use longer timeout for touch devices
            delay = player.touch ? 3000 : 2000;
          }

          // Clear timer
          clearTimeout(timers.controls);

          // Set new timer to prevent flicker when seeking
          timers.controls = setTimeout(() => ui.toggleControls.call(player, false), delay);
        });

        // Set a gutter for Vimeo
        const setGutter = () => {
          if (!player.isVimeo || player.config.vimeo.premium) {
            return;
          }
          const target = elements.wrapper;
          const {
            active
          } = player.fullscreen;
          const [videoWidth, videoHeight] = getAspectRatio.call(player);
          const useNativeAspectRatio = supportsCSS(`aspect-ratio: ${videoWidth} / ${videoHeight}`);

          // If not active, remove styles
          if (!active) {
            if (useNativeAspectRatio) {
              target.style.width = null;
              target.style.height = null;
            } else {
              target.style.maxWidth = null;
              target.style.margin = null;
            }
            return;
          }

          // Determine which dimension will overflow and constrain view
          const [viewportWidth, viewportHeight] = getViewportSize();
          const overflow = viewportWidth / viewportHeight > videoWidth / videoHeight;
          if (useNativeAspectRatio) {
            target.style.width = overflow ? 'auto' : '100%';
            target.style.height = overflow ? '100%' : 'auto';
          } else {
            target.style.maxWidth = overflow ? `${viewportHeight / videoHeight * videoWidth}px` : null;
            target.style.margin = overflow ? '0 auto' : null;
          }
        };

        // Handle resizing
        const resized = () => {
          clearTimeout(timers.resized);
          timers.resized = setTimeout(setGutter, 50);
        };
        on.call(player, elements.container, 'enterfullscreen exitfullscreen', event => {
          const {
            target
          } = player.fullscreen;

          // Ignore events not from target
          if (target !== elements.container) {
            return;
          }

          // If it's not an embed and no ratio specified
          if (!player.isEmbed && is.empty(player.config.ratio)) {
            return;
          }

          // Set Vimeo gutter
          setGutter();

          // Watch for resizes
          const method = event.type === 'enterfullscreen' ? on : off;
          method.call(player, window, 'resize', resized);
        });
      });
      // Listen for media events
      _defineProperty$1(this, "media", () => {
        const {
          player
        } = this;
        const {
          elements
        } = player;

        // Time change on media
        on.call(player, player.media, 'timeupdate seeking seeked', event => controls.timeUpdate.call(player, event));

        // Display duration
        on.call(player, player.media, 'durationchange loadeddata loadedmetadata', event => controls.durationUpdate.call(player, event));

        // Handle the media finishing
        on.call(player, player.media, 'ended', () => {
          // Show poster on end
          if (player.isHTML5 && player.isVideo && player.config.resetOnEnd) {
            // Restart
            player.restart();

            // Call pause otherwise IE11 will start playing the video again
            player.pause();
          }
        });

        // Check for buffer progress
        on.call(player, player.media, 'progress playing seeking seeked', event => controls.updateProgress.call(player, event));

        // Handle volume changes
        on.call(player, player.media, 'volumechange', event => controls.updateVolume.call(player, event));

        // Handle play/pause
        on.call(player, player.media, 'playing play pause ended emptied timeupdate', event => ui.checkPlaying.call(player, event));

        // Loading state
        on.call(player, player.media, 'waiting canplay seeked playing', event => ui.checkLoading.call(player, event));

        // Click video
        if (player.supported.ui && player.config.clickToPlay && !player.isAudio) {
          // Re-fetch the wrapper
          const wrapper = getElement.call(player, `.${player.config.classNames.video}`);

          // Bail if there's no wrapper (this should never happen)
          if (!is.element(wrapper)) {
            return;
          }

          // On click play, pause or restart
          on.call(player, elements.container, 'click', event => {
            const targets = [elements.container, wrapper];

            // Ignore if click if not container or in video wrapper
            if (!targets.includes(event.target) && !wrapper.contains(event.target)) {
              return;
            }

            // Touch devices will just show controls (if hidden)
            if (player.touch && player.config.hideControls) {
              return;
            }
            if (player.ended) {
              this.proxy(event, player.restart, 'restart');
              this.proxy(event, () => {
                silencePromise(player.play());
              }, 'play');
            } else {
              this.proxy(event, () => {
                silencePromise(player.togglePlay());
              }, 'play');
            }
          });
        }

        // Disable right click
        if (player.supported.ui && player.config.disableContextMenu) {
          on.call(player, elements.wrapper, 'contextmenu', event => {
            event.preventDefault();
          }, false);
        }

        // Volume change
        on.call(player, player.media, 'volumechange', () => {
          // Save to storage
          player.storage.set({
            volume: player.volume,
            muted: player.muted
          });
        });

        // Speed change
        on.call(player, player.media, 'ratechange', () => {
          // Update UI
          controls.updateSetting.call(player, 'speed');

          // Save to storage
          player.storage.set({
            speed: player.speed
          });
        });

        // Quality change
        on.call(player, player.media, 'qualitychange', event => {
          // Update UI
          controls.updateSetting.call(player, 'quality', null, event.detail.quality);
        });

        // Update download link when ready and if quality changes
        on.call(player, player.media, 'ready qualitychange', () => {
          controls.setDownloadUrl.call(player);
        });

        // Proxy events to container
        // Bubble up key events for Edge
        const proxyEvents = player.config.events.concat(['keyup', 'keydown']).join(' ');
        on.call(player, player.media, proxyEvents, event => {
          let {
            detail = {}
          } = event;

          // Get error details from media
          if (event.type === 'error') {
            detail = player.media.error;
          }
          triggerEvent.call(player, elements.container, event.type, true, detail);
        });
      });
      // Run default and custom handlers
      _defineProperty$1(this, "proxy", (event, defaultHandler, customHandlerKey) => {
        const {
          player
        } = this;
        const customHandler = player.config.listeners[customHandlerKey];
        const hasCustomHandler = is.function(customHandler);
        let returned = true;

        // Execute custom handler
        if (hasCustomHandler) {
          returned = customHandler.call(player, event);
        }

        // Only call default handler if not prevented in custom handler
        if (returned !== false && is.function(defaultHandler)) {
          defaultHandler.call(player, event);
        }
      });
      // Trigger custom and default handlers
      _defineProperty$1(this, "bind", (element, type, defaultHandler, customHandlerKey, passive = true) => {
        const {
          player
        } = this;
        const customHandler = player.config.listeners[customHandlerKey];
        const hasCustomHandler = is.function(customHandler);
        on.call(player, element, type, event => this.proxy(event, defaultHandler, customHandlerKey), passive && !hasCustomHandler);
      });
      // Listen for control events
      _defineProperty$1(this, "controls", () => {
        const {
          player
        } = this;
        const {
          elements
        } = player;
        // IE doesn't support input event, so we fallback to change
        const inputEvent = browser.isIE ? 'change' : 'input';

        // Play/pause toggle
        if (elements.buttons.play) {
          Array.from(elements.buttons.play).forEach(button => {
            this.bind(button, 'click', () => {
              silencePromise(player.togglePlay());
            }, 'play');
          });
        }

        // Pause
        this.bind(elements.buttons.restart, 'click', player.restart, 'restart');

        // Rewind
        this.bind(elements.buttons.rewind, 'click', () => {
          // Record seek time so we can prevent hiding controls for a few seconds after rewind
          player.lastSeekTime = Date.now();
          player.rewind();
        }, 'rewind');

        // Rewind
        this.bind(elements.buttons.fastForward, 'click', () => {
          // Record seek time so we can prevent hiding controls for a few seconds after fast forward
          player.lastSeekTime = Date.now();
          player.forward();
        }, 'fastForward');

        // Mute toggle
        this.bind(elements.buttons.mute, 'click', () => {
          player.muted = !player.muted;
        }, 'mute');

        // Captions toggle
        this.bind(elements.buttons.captions, 'click', () => player.toggleCaptions());

        // Download
        this.bind(elements.buttons.download, 'click', () => {
          triggerEvent.call(player, player.media, 'download');
        }, 'download');

        // Fullscreen toggle
        this.bind(elements.buttons.fullscreen, 'click', () => {
          player.fullscreen.toggle();
        }, 'fullscreen');

        // Picture-in-Picture
        this.bind(elements.buttons.pip, 'click', () => {
          player.pip = 'toggle';
        }, 'pip');

        // Airplay
        this.bind(elements.buttons.airplay, 'click', player.airplay, 'airplay');

        // Settings menu - click toggle
        this.bind(elements.buttons.settings, 'click', event => {
          // Prevent the document click listener closing the menu
          event.stopPropagation();
          event.preventDefault();
          controls.toggleMenu.call(player, event);
        }, null, false); // Can't be passive as we're preventing default

        // Settings menu - keyboard toggle
        // We have to bind to keyup otherwise Firefox triggers a click when a keydown event handler shifts focus
        // https://bugzilla.mozilla.org/show_bug.cgi?id=1220143
        this.bind(elements.buttons.settings, 'keyup', event => {
          if (![' ', 'Enter'].includes(event.key)) {
            return;
          }

          // Because return triggers a click anyway, all we need to do is set focus
          if (event.key === 'Enter') {
            controls.focusFirstMenuItem.call(player, null, true);
            return;
          }

          // Prevent scroll
          event.preventDefault();

          // Prevent playing video (Firefox)
          event.stopPropagation();

          // Toggle menu
          controls.toggleMenu.call(player, event);
        }, null, false // Can't be passive as we're preventing default
        );

        // Escape closes menu
        this.bind(elements.settings.menu, 'keydown', event => {
          if (event.key === 'Escape') {
            controls.toggleMenu.call(player, event);
          }
        });

        // Set range input alternative "value", which matches the tooltip time (#954)
        this.bind(elements.inputs.seek, 'mousedown mousemove', event => {
          const rect = elements.progress.getBoundingClientRect();
          const percent = 100 / rect.width * (event.pageX - rect.left);
          event.currentTarget.setAttribute('seek-value', percent);
        });

        // Pause while seeking
        this.bind(elements.inputs.seek, 'mousedown mouseup keydown keyup touchstart touchend', event => {
          const seek = event.currentTarget;
          const attribute = 'play-on-seeked';
          if (is.keyboardEvent(event) && !['ArrowLeft', 'ArrowRight'].includes(event.key)) {
            return;
          }

          // Record seek time so we can prevent hiding controls for a few seconds after seek
          player.lastSeekTime = Date.now();

          // Was playing before?
          const play = seek.hasAttribute(attribute);
          // Done seeking
          const done = ['mouseup', 'touchend', 'keyup'].includes(event.type);

          // If we're done seeking and it was playing, resume playback
          if (play && done) {
            seek.removeAttribute(attribute);
            silencePromise(player.play());
          } else if (!done && player.playing) {
            seek.setAttribute(attribute, '');
            player.pause();
          }
        });

        // Fix range inputs on iOS
        // Super weird iOS bug where after you interact with an <input type="range">,
        // it takes over further interactions on the page. This is a hack
        if (browser.isIos) {
          const inputs = getElements.call(player, 'input[type="range"]');
          Array.from(inputs).forEach(input => this.bind(input, inputEvent, event => repaint(event.target)));
        }

        // Seek
        this.bind(elements.inputs.seek, inputEvent, event => {
          const seek = event.currentTarget;
          // If it exists, use seek-value instead of "value" for consistency with tooltip time (#954)
          let seekTo = seek.getAttribute('seek-value');
          if (is.empty(seekTo)) {
            seekTo = seek.value;
          }
          seek.removeAttribute('seek-value');
          player.currentTime = seekTo / seek.max * player.duration;
        }, 'seek');

        // Seek tooltip
        this.bind(elements.progress, 'mouseenter mouseleave mousemove', event => controls.updateSeekTooltip.call(player, event));

        // Preview thumbnails plugin
        // TODO: Really need to work on some sort of plug-in wide event bus or pub-sub for this
        this.bind(elements.progress, 'mousemove touchmove', event => {
          const {
            previewThumbnails
          } = player;
          if (previewThumbnails && previewThumbnails.loaded) {
            previewThumbnails.startMove(event);
          }
        });

        // Hide thumbnail preview - on mouse click, mouse leave, and video play/seek. All four are required, e.g., for buffering
        this.bind(elements.progress, 'mouseleave touchend click', () => {
          const {
            previewThumbnails
          } = player;
          if (previewThumbnails && previewThumbnails.loaded) {
            previewThumbnails.endMove(false, true);
          }
        });

        // Show scrubbing preview
        this.bind(elements.progress, 'mousedown touchstart', event => {
          const {
            previewThumbnails
          } = player;
          if (previewThumbnails && previewThumbnails.loaded) {
            previewThumbnails.startScrubbing(event);
          }
        });
        this.bind(elements.progress, 'mouseup touchend', event => {
          const {
            previewThumbnails
          } = player;
          if (previewThumbnails && previewThumbnails.loaded) {
            previewThumbnails.endScrubbing(event);
          }
        });

        // Polyfill for lower fill in <input type="range"> for webkit
        if (browser.isWebKit) {
          Array.from(getElements.call(player, 'input[type="range"]')).forEach(element => {
            this.bind(element, 'input', event => controls.updateRangeFill.call(player, event.target));
          });
        }

        // Current time invert
        // Only if one time element is used for both currentTime and duration
        if (player.config.toggleInvert && !is.element(elements.display.duration)) {
          this.bind(elements.display.currentTime, 'click', () => {
            // Do nothing if we're at the start
            if (player.currentTime === 0) {
              return;
            }
            player.config.invertTime = !player.config.invertTime;
            controls.timeUpdate.call(player);
          });
        }

        // Volume
        this.bind(elements.inputs.volume, inputEvent, event => {
          player.volume = event.target.value;
        }, 'volume');

        // Update controls.hover state (used for ui.toggleControls to avoid hiding when interacting)
        this.bind(elements.controls, 'mouseenter mouseleave', event => {
          elements.controls.hover = !player.touch && event.type === 'mouseenter';
        });

        // Also update controls.hover state for any non-player children of fullscreen element (as above)
        if (elements.fullscreen) {
          Array.from(elements.fullscreen.children).filter(c => !c.contains(elements.container)).forEach(child => {
            this.bind(child, 'mouseenter mouseleave', event => {
              if (elements.controls) {
                elements.controls.hover = !player.touch && event.type === 'mouseenter';
              }
            });
          });
        }

        // Update controls.pressed state (used for ui.toggleControls to avoid hiding when interacting)
        this.bind(elements.controls, 'mousedown mouseup touchstart touchend touchcancel', event => {
          elements.controls.pressed = ['mousedown', 'touchstart'].includes(event.type);
        });

        // Show controls when they receive focus (e.g., when using keyboard tab key)
        this.bind(elements.controls, 'focusin', () => {
          const {
            config,
            timers
          } = player;

          // Skip transition to prevent focus from scrolling the parent element
          toggleClass(elements.controls, config.classNames.noTransition, true);

          // Toggle
          ui.toggleControls.call(player, true);

          // Restore transition
          setTimeout(() => {
            toggleClass(elements.controls, config.classNames.noTransition, false);
          }, 0);

          // Delay a little more for mouse users
          const delay = this.touch ? 3000 : 4000;

          // Clear timer
          clearTimeout(timers.controls);

          // Hide again after delay
          timers.controls = setTimeout(() => ui.toggleControls.call(player, false), delay);
        });

        // Mouse wheel for volume
        this.bind(elements.inputs.volume, 'wheel', event => {
          // Detect "natural" scroll - supported on OS X Safari only
          // Other browsers on OS X will be inverted until support improves
          const inverted = event.webkitDirectionInvertedFromDevice;
          // Get delta from event. Invert if `inverted` is true
          const [x, y] = [event.deltaX, -event.deltaY].map(value => inverted ? -value : value);
          // Using the biggest delta, normalize to 1 or -1 (or 0 if no delta)
          const direction = Math.sign(Math.abs(x) > Math.abs(y) ? x : y);

          // Change the volume by 2%
          player.increaseVolume(direction / 50);

          // Don't break page scrolling at max and min
          const {
            volume
          } = player.media;
          if (direction === 1 && volume < 1 || direction === -1 && volume > 0) {
            event.preventDefault();
          }
        }, 'volume', false);
      });
      this.player = _player;
      this.lastKey = null;
      this.focusTimer = null;
      this.lastKeyDown = null;
      this.handleKey = this.handleKey.bind(this);
      this.toggleMenu = this.toggleMenu.bind(this);
      this.firstTouch = this.firstTouch.bind(this);
    }

    // Handle key presses
    handleKey(event) {
      const {
        player
      } = this;
      const {
        elements
      } = player;
      const {
        key,
        type,
        altKey,
        ctrlKey,
        metaKey,
        shiftKey
      } = event;
      const pressed = type === 'keydown';
      const repeat = pressed && key === this.lastKey;

      // Bail if a modifier key is set
      if (altKey || ctrlKey || metaKey || shiftKey) {
        return;
      }

      // If the event is bubbled from the media element
      // Firefox doesn't get the key for whatever reason
      if (!key) {
        return;
      }

      // Seek by increment
      const seekByIncrement = increment => {
        // Divide the max duration into 10th's and times by the number value
        player.currentTime = player.duration / 10 * increment;
      };

      // Handle the key on keydown
      // Reset on keyup
      if (pressed) {
        // Check focused element
        // and if the focused element is not editable (e.g. text input)
        // and any that accept key input http://webaim.org/techniques/keyboard/
        const focused = document.activeElement;
        if (is.element(focused)) {
          const {
            editable
          } = player.config.selectors;
          const {
            seek
          } = elements.inputs;
          if (focused !== seek && matches(focused, editable)) {
            return;
          }
          if (event.key === ' ' && matches(focused, 'button, [role^="menuitem"]')) {
            return;
          }
        }

        // Which keys should we prevent default
        const preventDefault = [' ', 'ArrowLeft', 'ArrowUp', 'ArrowRight', 'ArrowDown', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'c', 'f', 'k', 'l', 'm'];

        // If the key is found prevent default (e.g. prevent scrolling for arrows)
        if (preventDefault.includes(key)) {
          event.preventDefault();
          event.stopPropagation();
        }
        switch (key) {
          case '0':
          case '1':
          case '2':
          case '3':
          case '4':
          case '5':
          case '6':
          case '7':
          case '8':
          case '9':
            if (!repeat) {
              seekByIncrement(parseInt(key, 10));
            }
            break;
          case ' ':
          case 'k':
            if (!repeat) {
              silencePromise(player.togglePlay());
            }
            break;
          case 'ArrowUp':
            player.increaseVolume(0.1);
            break;
          case 'ArrowDown':
            player.decreaseVolume(0.1);
            break;
          case 'm':
            if (!repeat) {
              player.muted = !player.muted;
            }
            break;
          case 'ArrowRight':
            player.forward();
            break;
          case 'ArrowLeft':
            player.rewind();
            break;
          case 'f':
            player.fullscreen.toggle();
            break;
          case 'c':
            if (!repeat) {
              player.toggleCaptions();
            }
            break;
          case 'l':
            player.loop = !player.loop;
            break;
        }

        // Escape is handle natively when in full screen
        // So we only need to worry about non native
        if (key === 'Escape' && !player.fullscreen.usingNative && player.fullscreen.active) {
          player.fullscreen.toggle();
        }

        // Store last key for next cycle
        this.lastKey = key;
      } else {
        this.lastKey = null;
      }
    }

    // Toggle menu
    toggleMenu(event) {
      controls.toggleMenu.call(this.player, event);
    }
  }

  var commonjsGlobal = typeof globalThis !== 'undefined' ? globalThis : typeof window !== 'undefined' ? window : typeof global !== 'undefined' ? global : typeof self !== 'undefined' ? self : {};

  function createCommonjsModule(fn, module) {
  	return module = { exports: {} }, fn(module, module.exports), module.exports;
  }

  var loadjs_umd = createCommonjsModule(function (module, exports) {
    (function (root, factory) {
      {
        module.exports = factory();
      }
    })(commonjsGlobal, function () {
      /**
       * Global dependencies.
       * @global {Object} document - DOM
       */

      var devnull = function () {},
        bundleIdCache = {},
        bundleResultCache = {},
        bundleCallbackQueue = {};

      /**
       * Subscribe to bundle load event.
       * @param {string[]} bundleIds - Bundle ids
       * @param {Function} callbackFn - The callback function
       */
      function subscribe(bundleIds, callbackFn) {
        // listify
        bundleIds = bundleIds.push ? bundleIds : [bundleIds];
        var depsNotFound = [],
          i = bundleIds.length,
          numWaiting = i,
          fn,
          bundleId,
          r,
          q;

        // define callback function
        fn = function (bundleId, pathsNotFound) {
          if (pathsNotFound.length) depsNotFound.push(bundleId);
          numWaiting--;
          if (!numWaiting) callbackFn(depsNotFound);
        };

        // register callback
        while (i--) {
          bundleId = bundleIds[i];

          // execute callback if in result cache
          r = bundleResultCache[bundleId];
          if (r) {
            fn(bundleId, r);
            continue;
          }

          // add to callback queue
          q = bundleCallbackQueue[bundleId] = bundleCallbackQueue[bundleId] || [];
          q.push(fn);
        }
      }

      /**
       * Publish bundle load event.
       * @param {string} bundleId - Bundle id
       * @param {string[]} pathsNotFound - List of files not found
       */
      function publish(bundleId, pathsNotFound) {
        // exit if id isn't defined
        if (!bundleId) return;
        var q = bundleCallbackQueue[bundleId];

        // cache result
        bundleResultCache[bundleId] = pathsNotFound;

        // exit if queue is empty
        if (!q) return;

        // empty callback queue
        while (q.length) {
          q[0](bundleId, pathsNotFound);
          q.splice(0, 1);
        }
      }

      /**
       * Execute callbacks.
       * @param {Object or Function} args - The callback args
       * @param {string[]} depsNotFound - List of dependencies not found
       */
      function executeCallbacks(args, depsNotFound) {
        // accept function as argument
        if (args.call) args = {
          success: args
        };

        // success and error callbacks
        if (depsNotFound.length) (args.error || devnull)(depsNotFound);else (args.success || devnull)(args);
      }

      /**
       * Load individual file.
       * @param {string} path - The file path
       * @param {Function} callbackFn - The callback function
       */
      function loadFile(path, callbackFn, args, numTries) {
        var doc = document,
          async = args.async,
          maxTries = (args.numRetries || 0) + 1,
          beforeCallbackFn = args.before || devnull,
          pathname = path.replace(/[\?|#].*$/, ''),
          pathStripped = path.replace(/^(css|img)!/, ''),
          isLegacyIECss,
          e;
        numTries = numTries || 0;
        if (/(^css!|\.css$)/.test(pathname)) {
          // css
          e = doc.createElement('link');
          e.rel = 'stylesheet';
          e.href = pathStripped;

          // tag IE9+
          isLegacyIECss = 'hideFocus' in e;

          // use preload in IE Edge (to detect load errors)
          if (isLegacyIECss && e.relList) {
            isLegacyIECss = 0;
            e.rel = 'preload';
            e.as = 'style';
          }
        } else if (/(^img!|\.(png|gif|jpg|svg|webp)$)/.test(pathname)) {
          // image
          e = doc.createElement('img');
          e.src = pathStripped;
        } else {
          // javascript
          e = doc.createElement('script');
          e.src = path;
          e.async = async === undefined ? true : async;
        }
        e.onload = e.onerror = e.onbeforeload = function (ev) {
          var result = ev.type[0];

          // treat empty stylesheets as failures to get around lack of onerror
          // support in IE9-11
          if (isLegacyIECss) {
            try {
              if (!e.sheet.cssText.length) result = 'e';
            } catch (x) {
              // sheets objects created from load errors don't allow access to
              // `cssText` (unless error is Code:18 SecurityError)
              if (x.code != 18) result = 'e';
            }
          }

          // handle retries in case of load failure
          if (result == 'e') {
            // increment counter
            numTries += 1;

            // exit function and try again
            if (numTries < maxTries) {
              return loadFile(path, callbackFn, args, numTries);
            }
          } else if (e.rel == 'preload' && e.as == 'style') {
            // activate preloaded stylesheets
            return e.rel = 'stylesheet'; // jshint ignore:line
          }

          // execute callback
          callbackFn(path, result, ev.defaultPrevented);
        };

        // add to document (unless callback returns `false`)
        if (beforeCallbackFn(path, e) !== false) doc.head.appendChild(e);
      }

      /**
       * Load multiple files.
       * @param {string[]} paths - The file paths
       * @param {Function} callbackFn - The callback function
       */
      function loadFiles(paths, callbackFn, args) {
        // listify paths
        paths = paths.push ? paths : [paths];
        var numWaiting = paths.length,
          x = numWaiting,
          pathsNotFound = [],
          fn,
          i;

        // define callback function
        fn = function (path, result, defaultPrevented) {
          // handle error
          if (result == 'e') pathsNotFound.push(path);

          // handle beforeload event. If defaultPrevented then that means the load
          // will be blocked (ex. Ghostery/ABP on Safari)
          if (result == 'b') {
            if (defaultPrevented) pathsNotFound.push(path);else return;
          }
          numWaiting--;
          if (!numWaiting) callbackFn(pathsNotFound);
        };

        // load scripts
        for (i = 0; i < x; i++) loadFile(paths[i], fn, args);
      }

      /**
       * Initiate script load and register bundle.
       * @param {(string|string[])} paths - The file paths
       * @param {(string|Function|Object)} [arg1] - The (1) bundleId or (2) success
       *   callback or (3) object literal with success/error arguments, numRetries,
       *   etc.
       * @param {(Function|Object)} [arg2] - The (1) success callback or (2) object
       *   literal with success/error arguments, numRetries, etc.
       */
      function loadjs(paths, arg1, arg2) {
        var bundleId, args;

        // bundleId (if string)
        if (arg1 && arg1.trim) bundleId = arg1;

        // args (default is {})
        args = (bundleId ? arg2 : arg1) || {};

        // throw error if bundle is already defined
        if (bundleId) {
          if (bundleId in bundleIdCache) {
            throw "LoadJS";
          } else {
            bundleIdCache[bundleId] = true;
          }
        }
        function loadFn(resolve, reject) {
          loadFiles(paths, function (pathsNotFound) {
            // execute callbacks
            executeCallbacks(args, pathsNotFound);

            // resolve Promise
            if (resolve) {
              executeCallbacks({
                success: resolve,
                error: reject
              }, pathsNotFound);
            }

            // publish bundle load event
            publish(bundleId, pathsNotFound);
          }, args);
        }
        if (args.returnPromise) return new Promise(loadFn);else loadFn();
      }

      /**
       * Execute callbacks when dependencies have been satisfied.
       * @param {(string|string[])} deps - List of bundle ids
       * @param {Object} args - success/error arguments
       */
      loadjs.ready = function ready(deps, args) {
        // subscribe to bundle load event
        subscribe(deps, function (depsNotFound) {
          // execute callbacks
          executeCallbacks(args, depsNotFound);
        });
        return loadjs;
      };

      /**
       * Manually satisfy bundle dependencies.
       * @param {string} bundleId - The bundle id
       */
      loadjs.done = function done(bundleId) {
        publish(bundleId, []);
      };

      /**
       * Reset loadjs dependencies statuses
       */
      loadjs.reset = function reset() {
        bundleIdCache = {};
        bundleResultCache = {};
        bundleCallbackQueue = {};
      };

      /**
       * Determine if bundle has already been defined
       * @param String} bundleId - The bundle id
       */
      loadjs.isDefined = function isDefined(bundleId) {
        return bundleId in bundleIdCache;
      };

      // export
      return loadjs;
    });
  });

  // ==========================================================================
  function loadScript(url) {
    return new Promise((resolve, reject) => {
      loadjs_umd(url, {
        success: resolve,
        error: reject
      });
    });
  }

  // ==========================================================================

  // Parse Vimeo ID from URL
  function parseId$1(url) {
    if (is.empty(url)) {
      return null;
    }
    if (is.number(Number(url))) {
      return url;
    }
    const regex = /^.*(vimeo.com\/|video\/)(\d+).*/;
    return url.match(regex) ? RegExp.$2 : url;
  }

  // Try to extract a hash for private videos from the URL
  function parseHash(url) {
    /* This regex matches a hexadecimal hash if given in any of these forms:
     *  - [https://player.]vimeo.com/video/{id}/{hash}[?params]
     *  - [https://player.]vimeo.com/video/{id}?h={hash}[&params]
     *  - [https://player.]vimeo.com/video/{id}?[params]&h={hash}
     *  - video/{id}/{hash}
     * If matched, the hash is available in capture group 4
     */
    const regex = /^.*(vimeo.com\/|video\/)(\d+)(\?.*&*h=|\/)+([\d,a-f]+)/;
    const found = url.match(regex);
    return found && found.length === 5 ? found[4] : null;
  }

  // Set playback state and trigger change (only on actual change)
  function assurePlaybackState$1(play) {
    if (play && !this.embed.hasPlayed) {
      this.embed.hasPlayed = true;
    }
    if (this.media.paused === play) {
      this.media.paused = !play;
      triggerEvent.call(this, this.media, play ? 'play' : 'pause');
    }
  }
  const vimeo = {
    setup() {
      const player = this;

      // Add embed class for responsive
      toggleClass(player.elements.wrapper, player.config.classNames.embed, true);

      // Set speed options from config
      player.options.speed = player.config.speed.options;

      // Set intial ratio
      setAspectRatio.call(player);

      // Load the SDK if not already
      if (!is.object(window.Vimeo)) {
        loadScript(player.config.urls.vimeo.sdk).then(() => {
          vimeo.ready.call(player);
        }).catch(error => {
          player.debug.warn('Vimeo SDK (player.js) failed to load', error);
        });
      } else {
        vimeo.ready.call(player);
      }
    },
    // API Ready
    ready() {
      const player = this;
      const config = player.config.vimeo;
      const {
        premium,
        referrerPolicy,
        ...frameParams
      } = config;
      // Get the source URL or ID
      let source = player.media.getAttribute('src');
      let hash = '';
      // Get from <div> if needed
      if (is.empty(source)) {
        source = player.media.getAttribute(player.config.attributes.embed.id);
        // hash can also be set as attribute on the <div>
        hash = player.media.getAttribute(player.config.attributes.embed.hash);
      } else {
        hash = parseHash(source);
      }
      const hashParam = hash ? {
        h: hash
      } : {};

      // If the owner has a pro or premium account then we can hide controls etc
      if (premium) {
        Object.assign(frameParams, {
          controls: false,
          sidedock: false
        });
      }

      // Get Vimeo params for the iframe
      const params = buildUrlParams({
        loop: player.config.loop.active,
        autoplay: player.autoplay,
        muted: player.muted,
        gesture: 'media',
        playsinline: player.config.playsinline,
        // hash has to be added to iframe-URL
        ...hashParam,
        ...frameParams
      });
      const id = parseId$1(source);
      // Build an iframe
      const iframe = createElement('iframe');
      const src = format(player.config.urls.vimeo.iframe, id, params);
      iframe.setAttribute('src', src);
      iframe.setAttribute('allowfullscreen', '');
      iframe.setAttribute('allow', ['autoplay', 'fullscreen', 'picture-in-picture', 'encrypted-media', 'accelerometer', 'gyroscope'].join('; '));

      // Set the referrer policy if required
      if (!is.empty(referrerPolicy)) {
        iframe.setAttribute('referrerPolicy', referrerPolicy);
      }

      // Inject the package
      if (premium || !config.customControls) {
        iframe.setAttribute('data-poster', player.poster);
        player.media = replaceElement(iframe, player.media);
      } else {
        const wrapper = createElement('div', {
          class: player.config.classNames.embedContainer,
          'data-poster': player.poster
        });
        wrapper.appendChild(iframe);
        player.media = replaceElement(wrapper, player.media);
      }

      // Get poster image
      if (!config.customControls) {
        fetch(format(player.config.urls.vimeo.api, src)).then(response => {
          if (is.empty(response) || !response.thumbnail_url) {
            return;
          }

          // Set and show poster
          ui.setPoster.call(player, response.thumbnail_url).catch(() => {});
        });
      }

      // Setup instance
      // https://github.com/vimeo/player.js
      player.embed = new window.Vimeo.Player(iframe, {
        autopause: player.config.autopause,
        muted: player.muted
      });
      player.media.paused = true;
      player.media.currentTime = 0;

      // Disable native text track rendering
      if (player.supported.ui) {
        player.embed.disableTextTrack();
      }

      // Create a faux HTML5 API using the Vimeo API
      player.media.play = () => {
        assurePlaybackState$1.call(player, true);
        return player.embed.play();
      };
      player.media.pause = () => {
        assurePlaybackState$1.call(player, false);
        return player.embed.pause();
      };
      player.media.stop = () => {
        player.pause();
        player.currentTime = 0;
      };

      // Seeking
      let {
        currentTime
      } = player.media;
      Object.defineProperty(player.media, 'currentTime', {
        get() {
          return currentTime;
        },
        set(time) {
          // Vimeo will automatically play on seek if the video hasn't been played before

          // Get current paused state and volume etc
          const {
            embed,
            media,
            paused,
            volume
          } = player;
          const restorePause = paused && !embed.hasPlayed;

          // Set seeking state and trigger event
          media.seeking = true;
          triggerEvent.call(player, media, 'seeking');

          // If paused, mute until seek is complete
          Promise.resolve(restorePause && embed.setVolume(0))
          // Seek
          .then(() => embed.setCurrentTime(time))
          // Restore paused
          .then(() => restorePause && embed.pause())
          // Restore volume
          .then(() => restorePause && embed.setVolume(volume)).catch(() => {
            // Do nothing
          });
        }
      });

      // Playback speed
      let speed = player.config.speed.selected;
      Object.defineProperty(player.media, 'playbackRate', {
        get() {
          return speed;
        },
        set(input) {
          player.embed.setPlaybackRate(input).then(() => {
            speed = input;
            triggerEvent.call(player, player.media, 'ratechange');
          }).catch(() => {
            // Cannot set Playback Rate, Video is probably not on Pro account
            player.options.speed = [1];
          });
        }
      });

      // Volume
      let {
        volume
      } = player.config;
      Object.defineProperty(player.media, 'volume', {
        get() {
          return volume;
        },
        set(input) {
          player.embed.setVolume(input).then(() => {
            volume = input;
            triggerEvent.call(player, player.media, 'volumechange');
          });
        }
      });

      // Muted
      let {
        muted
      } = player.config;
      Object.defineProperty(player.media, 'muted', {
        get() {
          return muted;
        },
        set(input) {
          const toggle = is.boolean(input) ? input : false;
          player.embed.setMuted(toggle ? true : player.config.muted).then(() => {
            muted = toggle;
            triggerEvent.call(player, player.media, 'volumechange');
          });
        }
      });

      // Loop
      let {
        loop
      } = player.config;
      Object.defineProperty(player.media, 'loop', {
        get() {
          return loop;
        },
        set(input) {
          const toggle = is.boolean(input) ? input : player.config.loop.active;
          player.embed.setLoop(toggle).then(() => {
            loop = toggle;
          });
        }
      });

      // Source
      let currentSrc;
      player.embed.getVideoUrl().then(value => {
        currentSrc = value;
        controls.setDownloadUrl.call(player);
      }).catch(error => {
        this.debug.warn(error);
      });
      Object.defineProperty(player.media, 'currentSrc', {
        get() {
          return currentSrc;
        }
      });

      // Ended
      Object.defineProperty(player.media, 'ended', {
        get() {
          return player.currentTime === player.duration;
        }
      });

      // Set aspect ratio based on video size
      Promise.all([player.embed.getVideoWidth(), player.embed.getVideoHeight()]).then(dimensions => {
        const [width, height] = dimensions;
        player.embed.ratio = roundAspectRatio(width, height);
        setAspectRatio.call(this);
      });

      // Set autopause
      player.embed.setAutopause(player.config.autopause).then(state => {
        player.config.autopause = state;
      });

      // Get title
      player.embed.getVideoTitle().then(title => {
        player.config.title = title;
        ui.setTitle.call(this);
      });

      // Get current time
      player.embed.getCurrentTime().then(value => {
        currentTime = value;
        triggerEvent.call(player, player.media, 'timeupdate');
      });

      // Get duration
      player.embed.getDuration().then(value => {
        player.media.duration = value;
        triggerEvent.call(player, player.media, 'durationchange');
      });

      // Get captions
      player.embed.getTextTracks().then(tracks => {
        player.media.textTracks = tracks;
        captions.setup.call(player);
      });
      player.embed.on('cuechange', ({
        cues = []
      }) => {
        const strippedCues = cues.map(cue => stripHTML(cue.text));
        captions.updateCues.call(player, strippedCues);
      });
      player.embed.on('loaded', () => {
        // Assure state and events are updated on autoplay
        player.embed.getPaused().then(paused => {
          assurePlaybackState$1.call(player, !paused);
          if (!paused) {
            triggerEvent.call(player, player.media, 'playing');
          }
        });
        if (is.element(player.embed.element) && player.supported.ui) {
          const frame = player.embed.element;

          // Fix keyboard focus issues
          // https://github.com/sampotts/plyr/issues/317
          frame.setAttribute('tabindex', -1);
        }
      });
      player.embed.on('bufferstart', () => {
        triggerEvent.call(player, player.media, 'waiting');
      });
      player.embed.on('bufferend', () => {
        triggerEvent.call(player, player.media, 'playing');
      });
      player.embed.on('play', () => {
        assurePlaybackState$1.call(player, true);
        triggerEvent.call(player, player.media, 'playing');
      });
      player.embed.on('pause', () => {
        assurePlaybackState$1.call(player, false);
      });
      player.embed.on('timeupdate', data => {
        player.media.seeking = false;
        currentTime = data.seconds;
        triggerEvent.call(player, player.media, 'timeupdate');
      });
      player.embed.on('progress', data => {
        player.media.buffered = data.percent;
        triggerEvent.call(player, player.media, 'progress');

        // Check all loaded
        if (parseInt(data.percent, 10) === 1) {
          triggerEvent.call(player, player.media, 'canplaythrough');
        }

        // Get duration as if we do it before load, it gives an incorrect value
        // https://github.com/sampotts/plyr/issues/891
        player.embed.getDuration().then(value => {
          if (value !== player.media.duration) {
            player.media.duration = value;
            triggerEvent.call(player, player.media, 'durationchange');
          }
        });
      });
      player.embed.on('seeked', () => {
        player.media.seeking = false;
        triggerEvent.call(player, player.media, 'seeked');
      });
      player.embed.on('ended', () => {
        player.media.paused = true;
        triggerEvent.call(player, player.media, 'ended');
      });
      player.embed.on('error', detail => {
        player.media.error = detail;
        triggerEvent.call(player, player.media, 'error');
      });

      // Rebuild UI
      if (config.customControls) {
        setTimeout(() => ui.build.call(player), 0);
      }
    }
  };

  // ==========================================================================

  // Parse YouTube ID from URL
  function parseId(url) {
    if (is.empty(url)) {
      return null;
    }
    const regex = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    return url.match(regex) ? RegExp.$2 : url;
  }

  // Set playback state and trigger change (only on actual change)
  function assurePlaybackState(play) {
    if (play && !this.embed.hasPlayed) {
      this.embed.hasPlayed = true;
    }
    if (this.media.paused === play) {
      this.media.paused = !play;
      triggerEvent.call(this, this.media, play ? 'play' : 'pause');
    }
  }
  function getHost(config) {
    if (config.noCookie) {
      return 'https://www.youtube-nocookie.com';
    }
    if (window.location.protocol === 'http:') {
      return 'http://www.youtube.com';
    }

    // Use YouTube's default
    return undefined;
  }
  const youtube = {
    setup() {
      // Add embed class for responsive
      toggleClass(this.elements.wrapper, this.config.classNames.embed, true);

      // Setup API
      if (is.object(window.YT) && is.function(window.YT.Player)) {
        youtube.ready.call(this);
      } else {
        // Reference current global callback
        const callback = window.onYouTubeIframeAPIReady;

        // Set callback to process queue
        window.onYouTubeIframeAPIReady = () => {
          // Call global callback if set
          if (is.function(callback)) {
            callback();
          }
          youtube.ready.call(this);
        };

        // Load the SDK
        loadScript(this.config.urls.youtube.sdk).catch(error => {
          this.debug.warn('YouTube API failed to load', error);
        });
      }
    },
    // Get the media title
    getTitle(videoId) {
      const url = format(this.config.urls.youtube.api, videoId);
      fetch(url).then(data => {
        if (is.object(data)) {
          const {
            title,
            height,
            width
          } = data;

          // Set title
          this.config.title = title;
          ui.setTitle.call(this);

          // Set aspect ratio
          this.embed.ratio = roundAspectRatio(width, height);
        }
        setAspectRatio.call(this);
      }).catch(() => {
        // Set aspect ratio
        setAspectRatio.call(this);
      });
    },
    // API ready
    ready() {
      const player = this;
      const config = player.config.youtube;
      // Ignore already setup (race condition)
      const currentId = player.media && player.media.getAttribute('id');
      if (!is.empty(currentId) && currentId.startsWith('youtube-')) {
        return;
      }

      // Get the source URL or ID
      let source = player.media.getAttribute('src');

      // Get from <div> if needed
      if (is.empty(source)) {
        source = player.media.getAttribute(this.config.attributes.embed.id);
      }

      // Replace the <iframe> with a <div> due to YouTube API issues
      const videoId = parseId(source);
      const id = generateId(player.provider);
      // Replace media element
      const container = createElement('div', {
        id,
        'data-poster': config.customControls ? player.poster : undefined
      });
      player.media = replaceElement(container, player.media);

      // Only load the poster when using custom controls
      if (config.customControls) {
        const posterSrc = s => `https://i.ytimg.com/vi/${videoId}/${s}default.jpg`;

        // Check thumbnail images in order of quality, but reject fallback thumbnails (120px wide)
        loadImage(posterSrc('maxres'), 121) // Highest quality and un-padded
        .catch(() => loadImage(posterSrc('sd'), 121)) // 480p padded 4:3
        .catch(() => loadImage(posterSrc('hq'))) // 360p padded 4:3. Always exists
        .then(image => ui.setPoster.call(player, image.src)).then(src => {
          // If the image is padded, use background-size "cover" instead (like youtube does too with their posters)
          if (!src.includes('maxres')) {
            player.elements.poster.style.backgroundSize = 'cover';
          }
        }).catch(() => {});
      }

      // Setup instance
      // https://developers.google.com/youtube/iframe_api_reference
      player.embed = new window.YT.Player(player.media, {
        videoId,
        host: getHost(config),
        playerVars: extend({}, {
          // Autoplay
          autoplay: player.config.autoplay ? 1 : 0,
          // iframe interface language
          hl: player.config.hl,
          // Only show controls if not fully supported or opted out
          controls: player.supported.ui && config.customControls ? 0 : 1,
          // Disable keyboard as we handle it
          disablekb: 1,
          // Allow iOS inline playback
          playsinline: player.config.playsinline && !player.config.fullscreen.iosNative ? 1 : 0,
          // Captions are flaky on YouTube
          cc_load_policy: player.captions.active ? 1 : 0,
          cc_lang_pref: player.config.captions.language,
          // Tracking for stats
          widget_referrer: window ? window.location.href : null
        }, config),
        events: {
          onError(event) {
            // YouTube may fire onError twice, so only handle it once
            if (!player.media.error) {
              const code = event.data;
              // Messages copied from https://developers.google.com/youtube/iframe_api_reference#onError
              const message = {
                2: 'The request contains an invalid parameter value. For example, this error occurs if you specify a video ID that does not have 11 characters, or if the video ID contains invalid characters, such as exclamation points or asterisks.',
                5: 'The requested content cannot be played in an HTML5 player or another error related to the HTML5 player has occurred.',
                100: 'The video requested was not found. This error occurs when a video has been removed (for any reason) or has been marked as private.',
                101: 'The owner of the requested video does not allow it to be played in embedded players.',
                150: 'The owner of the requested video does not allow it to be played in embedded players.'
              }[code] || 'An unknown error occurred';
              player.media.error = {
                code,
                message
              };
              triggerEvent.call(player, player.media, 'error');
            }
          },
          onPlaybackRateChange(event) {
            // Get the instance
            const instance = event.target;

            // Get current speed
            player.media.playbackRate = instance.getPlaybackRate();
            triggerEvent.call(player, player.media, 'ratechange');
          },
          onReady(event) {
            // Bail if onReady has already been called. See issue #1108
            if (is.function(player.media.play)) {
              return;
            }
            // Get the instance
            const instance = event.target;

            // Get the title
            youtube.getTitle.call(player, videoId);

            // Create a faux HTML5 API using the YouTube API
            player.media.play = () => {
              assurePlaybackState.call(player, true);
              instance.playVideo();
            };
            player.media.pause = () => {
              assurePlaybackState.call(player, false);
              instance.pauseVideo();
            };
            player.media.stop = () => {
              instance.stopVideo();
            };
            player.media.duration = instance.getDuration();
            player.media.paused = true;

            // Seeking
            player.media.currentTime = 0;
            Object.defineProperty(player.media, 'currentTime', {
              get() {
                return Number(instance.getCurrentTime());
              },
              set(time) {
                // If paused and never played, mute audio preventively (YouTube starts playing on seek if the video hasn't been played yet).
                if (player.paused && !player.embed.hasPlayed) {
                  player.embed.mute();
                }

                // Set seeking state and trigger event
                player.media.seeking = true;
                triggerEvent.call(player, player.media, 'seeking');

                // Seek after events sent
                instance.seekTo(time);
              }
            });

            // Playback speed
            Object.defineProperty(player.media, 'playbackRate', {
              get() {
                return instance.getPlaybackRate();
              },
              set(input) {
                instance.setPlaybackRate(input);
              }
            });

            // Volume
            let {
              volume
            } = player.config;
            Object.defineProperty(player.media, 'volume', {
              get() {
                return volume;
              },
              set(input) {
                volume = input;
                instance.setVolume(volume * 100);
                triggerEvent.call(player, player.media, 'volumechange');
              }
            });

            // Muted
            let {
              muted
            } = player.config;
            Object.defineProperty(player.media, 'muted', {
              get() {
                return muted;
              },
              set(input) {
                const toggle = is.boolean(input) ? input : muted;
                muted = toggle;
                instance[toggle ? 'mute' : 'unMute']();
                instance.setVolume(volume * 100);
                triggerEvent.call(player, player.media, 'volumechange');
              }
            });

            // Source
            Object.defineProperty(player.media, 'currentSrc', {
              get() {
                return instance.getVideoUrl();
              }
            });

            // Ended
            Object.defineProperty(player.media, 'ended', {
              get() {
                return player.currentTime === player.duration;
              }
            });

            // Get available speeds
            const speeds = instance.getAvailablePlaybackRates();
            // Filter based on config
            player.options.speed = speeds.filter(s => player.config.speed.options.includes(s));

            // Set the tabindex to avoid focus entering iframe
            if (player.supported.ui && config.customControls) {
              player.media.setAttribute('tabindex', -1);
            }
            triggerEvent.call(player, player.media, 'timeupdate');
            triggerEvent.call(player, player.media, 'durationchange');

            // Reset timer
            clearInterval(player.timers.buffering);

            // Setup buffering
            player.timers.buffering = setInterval(() => {
              // Get loaded % from YouTube
              player.media.buffered = instance.getVideoLoadedFraction();

              // Trigger progress only when we actually buffer something
              if (player.media.lastBuffered === null || player.media.lastBuffered < player.media.buffered) {
                triggerEvent.call(player, player.media, 'progress');
              }

              // Set last buffer point
              player.media.lastBuffered = player.media.buffered;

              // Bail if we're at 100%
              if (player.media.buffered === 1) {
                clearInterval(player.timers.buffering);

                // Trigger event
                triggerEvent.call(player, player.media, 'canplaythrough');
              }
            }, 200);

            // Rebuild UI
            if (config.customControls) {
              setTimeout(() => ui.build.call(player), 50);
            }
          },
          onStateChange(event) {
            // Get the instance
            const instance = event.target;

            // Reset timer
            clearInterval(player.timers.playing);
            const seeked = player.media.seeking && [1, 2].includes(event.data);
            if (seeked) {
              // Unset seeking and fire seeked event
              player.media.seeking = false;
              triggerEvent.call(player, player.media, 'seeked');
            }

            // Handle events
            // -1   Unstarted
            // 0    Ended
            // 1    Playing
            // 2    Paused
            // 3    Buffering
            // 5    Video cued
            switch (event.data) {
              case -1:
                // Update scrubber
                triggerEvent.call(player, player.media, 'timeupdate');

                // Get loaded % from YouTube
                player.media.buffered = instance.getVideoLoadedFraction();
                triggerEvent.call(player, player.media, 'progress');
                break;
              case 0:
                assurePlaybackState.call(player, false);

                // YouTube doesn't support loop for a single video, so mimick it.
                if (player.media.loop) {
                  // YouTube needs a call to `stopVideo` before playing again
                  instance.stopVideo();
                  instance.playVideo();
                } else {
                  triggerEvent.call(player, player.media, 'ended');
                }
                break;
              case 1:
                // Restore paused state (YouTube starts playing on seek if the video hasn't been played yet)
                if (config.customControls && !player.config.autoplay && player.media.paused && !player.embed.hasPlayed) {
                  player.media.pause();
                } else {
                  assurePlaybackState.call(player, true);
                  triggerEvent.call(player, player.media, 'playing');

                  // Poll to get playback progress
                  player.timers.playing = setInterval(() => {
                    triggerEvent.call(player, player.media, 'timeupdate');
                  }, 50);

                  // Check duration again due to YouTube bug
                  // https://github.com/sampotts/plyr/issues/374
                  // https://code.google.com/p/gdata-issues/issues/detail?id=8690
                  if (player.media.duration !== instance.getDuration()) {
                    player.media.duration = instance.getDuration();
                    triggerEvent.call(player, player.media, 'durationchange');
                  }
                }
                break;
              case 2:
                // Restore audio (YouTube starts playing on seek if the video hasn't been played yet)
                if (!player.muted) {
                  player.embed.unMute();
                }
                assurePlaybackState.call(player, false);
                break;
              case 3:
                // Trigger waiting event to add loading classes to container as the video buffers.
                triggerEvent.call(player, player.media, 'waiting');
                break;
            }
            triggerEvent.call(player, player.elements.container, 'statechange', false, {
              code: event.data
            });
          }
        }
      });
    }
  };

  // ==========================================================================
  const media = {
    // Setup media
    setup() {
      // If there's no media, bail
      if (!this.media) {
        this.debug.warn('No media element found!');
        return;
      }

      // Add type class
      toggleClass(this.elements.container, this.config.classNames.type.replace('{0}', this.type), true);

      // Add provider class
      toggleClass(this.elements.container, this.config.classNames.provider.replace('{0}', this.provider), true);

      // Add video class for embeds
      // This will require changes if audio embeds are added
      if (this.isEmbed) {
        toggleClass(this.elements.container, this.config.classNames.type.replace('{0}', 'video'), true);
      }

      // Inject the player wrapper
      if (this.isVideo) {
        // Create the wrapper div
        this.elements.wrapper = createElement('div', {
          class: this.config.classNames.video
        });

        // Wrap the video in a container
        wrap(this.media, this.elements.wrapper);

        // Poster image container
        this.elements.poster = createElement('div', {
          class: this.config.classNames.poster
        });
        this.elements.wrapper.appendChild(this.elements.poster);
      }
      if (this.isHTML5) {
        html5.setup.call(this);
      } else if (this.isYouTube) {
        youtube.setup.call(this);
      } else if (this.isVimeo) {
        vimeo.setup.call(this);
      }
    }
  };

  const destroy = instance => {
    // Destroy our adsManager
    if (instance.manager) {
      instance.manager.destroy();
    }

    // Destroy our adsManager
    if (instance.elements.displayContainer) {
      instance.elements.displayContainer.destroy();
    }
    instance.elements.container.remove();
  };
  class Ads {
    /**
     * Ads constructor.
     * @param {Object} player
     * @return {Ads}
     */
    constructor(player) {
      /**
       * Load the IMA SDK
       */
      _defineProperty$1(this, "load", () => {
        if (!this.enabled) {
          return;
        }

        // Check if the Google IMA3 SDK is loaded or load it ourselves
        if (!is.object(window.google) || !is.object(window.google.ima)) {
          loadScript(this.player.config.urls.googleIMA.sdk).then(() => {
            this.ready();
          }).catch(() => {
            // Script failed to load or is blocked
            this.trigger('error', new Error('Google IMA SDK failed to load'));
          });
        } else {
          this.ready();
        }
      });
      /**
       * Get the ads instance ready
       */
      _defineProperty$1(this, "ready", () => {
        // Double check we're enabled
        if (!this.enabled) {
          destroy(this);
        }

        // Start ticking our safety timer. If the whole advertisement
        // thing doesn't resolve within our set time; we bail
        this.startSafetyTimer(12000, 'ready()');

        // Clear the safety timer
        this.managerPromise.then(() => {
          this.clearSafetyTimer('onAdsManagerLoaded()');
        });

        // Set listeners on the Plyr instance
        this.listeners();

        // Setup the IMA SDK
        this.setupIMA();
      });
      /**
       * In order for the SDK to display ads for our video, we need to tell it where to put them,
       * so here we define our ad container. This div is set up to render on top of the video player.
       * Using the code below, we tell the SDK to render ads within that div. We also provide a
       * handle to the content video player - the SDK will poll the current time of our player to
       * properly place mid-rolls. After we create the ad display container, we initialize it. On
       * mobile devices, this initialization is done as the result of a user action.
       */
      _defineProperty$1(this, "setupIMA", () => {
        // Create the container for our advertisements
        this.elements.container = createElement('div', {
          class: this.player.config.classNames.ads
        });
        this.player.elements.container.appendChild(this.elements.container);

        // So we can run VPAID2
        google.ima.settings.setVpaidMode(google.ima.ImaSdkSettings.VpaidMode.ENABLED);

        // Set language
        google.ima.settings.setLocale(this.player.config.ads.language);

        // Set playback for iOS10+
        google.ima.settings.setDisableCustomPlaybackForIOS10Plus(this.player.config.playsinline);

        // We assume the adContainer is the video container of the plyr element that will house the ads
        this.elements.displayContainer = new google.ima.AdDisplayContainer(this.elements.container, this.player.media);

        // Create ads loader
        this.loader = new google.ima.AdsLoader(this.elements.displayContainer);

        // Listen and respond to ads loaded and error events
        this.loader.addEventListener(google.ima.AdsManagerLoadedEvent.Type.ADS_MANAGER_LOADED, event => this.onAdsManagerLoaded(event), false);
        this.loader.addEventListener(google.ima.AdErrorEvent.Type.AD_ERROR, error => this.onAdError(error), false);

        // Request video ads to be pre-loaded
        this.requestAds();
      });
      /**
       * Request advertisements
       */
      _defineProperty$1(this, "requestAds", () => {
        const {
          container
        } = this.player.elements;
        try {
          // Request video ads
          const request = new google.ima.AdsRequest();
          request.adTagUrl = this.tagUrl;

          // Specify the linear and nonlinear slot sizes. This helps the SDK
          // to select the correct creative if multiple are returned
          request.linearAdSlotWidth = container.offsetWidth;
          request.linearAdSlotHeight = container.offsetHeight;
          request.nonLinearAdSlotWidth = container.offsetWidth;
          request.nonLinearAdSlotHeight = container.offsetHeight;

          // We only overlay ads as we only support video.
          request.forceNonLinearFullSlot = false;

          // Mute based on current state
          request.setAdWillPlayMuted(!this.player.muted);
          this.loader.requestAds(request);
        } catch (error) {
          this.onAdError(error);
        }
      });
      /**
       * Update the ad countdown
       * @param {Boolean} start
       */
      _defineProperty$1(this, "pollCountdown", (start = false) => {
        if (!start) {
          clearInterval(this.countdownTimer);
          this.elements.container.removeAttribute('data-badge-text');
          return;
        }
        const update = () => {
          const time = formatTime(Math.max(this.manager.getRemainingTime(), 0));
          const label = `${i18n.get('advertisement', this.player.config)} - ${time}`;
          this.elements.container.setAttribute('data-badge-text', label);
        };
        this.countdownTimer = setInterval(update, 100);
      });
      /**
       * This method is called whenever the ads are ready inside the AdDisplayContainer
       * @param {Event} event - adsManagerLoadedEvent
       */
      _defineProperty$1(this, "onAdsManagerLoaded", event => {
        // Load could occur after a source change (race condition)
        if (!this.enabled) {
          return;
        }

        // Get the ads manager
        const settings = new google.ima.AdsRenderingSettings();

        // Tell the SDK to save and restore content video state on our behalf
        settings.restoreCustomPlaybackStateOnAdBreakComplete = true;
        settings.enablePreloading = true;

        // The SDK is polling currentTime on the contentPlayback. And needs a duration
        // so it can determine when to start the mid- and post-roll
        this.manager = event.getAdsManager(this.player, settings);

        // Get the cue points for any mid-rolls by filtering out the pre- and post-roll
        this.cuePoints = this.manager.getCuePoints();

        // Add listeners to the required events
        // Advertisement error events
        this.manager.addEventListener(google.ima.AdErrorEvent.Type.AD_ERROR, error => this.onAdError(error));

        // Advertisement regular events
        Object.keys(google.ima.AdEvent.Type).forEach(type => {
          this.manager.addEventListener(google.ima.AdEvent.Type[type], e => this.onAdEvent(e));
        });

        // Resolve our adsManager
        this.trigger('loaded');
      });
      _defineProperty$1(this, "addCuePoints", () => {
        // Add advertisement cue's within the time line if available
        if (!is.empty(this.cuePoints)) {
          this.cuePoints.forEach(cuePoint => {
            if (cuePoint !== 0 && cuePoint !== -1 && cuePoint < this.player.duration) {
              const seekElement = this.player.elements.progress;
              if (is.element(seekElement)) {
                const cuePercentage = 100 / this.player.duration * cuePoint;
                const cue = createElement('span', {
                  class: this.player.config.classNames.cues
                });
                cue.style.left = `${cuePercentage.toString()}%`;
                seekElement.appendChild(cue);
              }
            }
          });
        }
      });
      /**
       * This is where all the event handling takes place. Retrieve the ad from the event. Some
       * events (e.g. ALL_ADS_COMPLETED) don't have the ad object associated
       * https://developers.google.com/interactive-media-ads/docs/sdks/html5/v3/apis#ima.AdEvent.Type
       * @param {Event} event
       */
      _defineProperty$1(this, "onAdEvent", event => {
        const {
          container
        } = this.player.elements;
        // Retrieve the ad from the event. Some events (e.g. ALL_ADS_COMPLETED)
        // don't have ad object associated
        const ad = event.getAd();
        const adData = event.getAdData();

        // Proxy event
        const dispatchEvent = type => {
          triggerEvent.call(this.player, this.player.media, `ads${type.replace(/_/g, '').toLowerCase()}`);
        };

        // Bubble the event
        dispatchEvent(event.type);
        switch (event.type) {
          case google.ima.AdEvent.Type.LOADED:
            // This is the first event sent for an ad - it is possible to determine whether the
            // ad is a video ad or an overlay
            this.trigger('loaded');

            // Start countdown
            this.pollCountdown(true);
            if (!ad.isLinear()) {
              // Position AdDisplayContainer correctly for overlay
              ad.width = container.offsetWidth;
              ad.height = container.offsetHeight;
            }

            // console.info('Ad type: ' + event.getAd().getAdPodInfo().getPodIndex());
            // console.info('Ad time: ' + event.getAd().getAdPodInfo().getTimeOffset());

            break;
          case google.ima.AdEvent.Type.STARTED:
            // Set volume to match player
            this.manager.setVolume(this.player.volume);
            break;
          case google.ima.AdEvent.Type.ALL_ADS_COMPLETED:
            // All ads for the current videos are done. We can now request new advertisements
            // in case the video is re-played

            // TODO: Example for what happens when a next video in a playlist would be loaded.
            // So here we load a new video when all ads are done.
            // Then we load new ads within a new adsManager. When the video
            // Is started - after - the ads are loaded, then we get ads.
            // You can also easily test cancelling and reloading by running
            // player.ads.cancel() and player.ads.play from the console I guess.
            // this.player.source = {
            //     type: 'video',
            //     title: 'View From A Blue Moon',
            //     sources: [{
            //         src:
            // 'https://cdn.plyr.io/static/demo/View_From_A_Blue_Moon_Trailer-HD.mp4', type:
            // 'video/mp4', }], poster:
            // 'https://cdn.plyr.io/static/demo/View_From_A_Blue_Moon_Trailer-HD.jpg', tracks:
            // [ { kind: 'captions', label: 'English', srclang: 'en', src:
            // 'https://cdn.plyr.io/static/demo/View_From_A_Blue_Moon_Trailer-HD.en.vtt',
            // default: true, }, { kind: 'captions', label: 'French', srclang: 'fr', src:
            // 'https://cdn.plyr.io/static/demo/View_From_A_Blue_Moon_Trailer-HD.fr.vtt', }, ],
            // };

            // TODO: So there is still this thing where a video should only be allowed to start
            // playing when the IMA SDK is ready or has failed

            if (this.player.ended) {
              this.loadAds();
            } else {
              // The SDK won't allow new ads to be called without receiving a contentComplete()
              this.loader.contentComplete();
            }
            break;
          case google.ima.AdEvent.Type.CONTENT_PAUSE_REQUESTED:
            // This event indicates the ad has started - the video player can adjust the UI,
            // for example display a pause button and remaining time. Fired when content should
            // be paused. This usually happens right before an ad is about to cover the content

            this.pauseContent();
            break;
          case google.ima.AdEvent.Type.CONTENT_RESUME_REQUESTED:
            // This event indicates the ad has finished - the video player can perform
            // appropriate UI actions, such as removing the timer for remaining time detection.
            // Fired when content should be resumed. This usually happens when an ad finishes
            // or collapses

            this.pollCountdown();
            this.resumeContent();
            break;
          case google.ima.AdEvent.Type.LOG:
            if (adData.adError) {
              this.player.debug.warn(`Non-fatal ad error: ${adData.adError.getMessage()}`);
            }
            break;
        }
      });
      /**
       * Any ad error handling comes through here
       * @param {Event} event
       */
      _defineProperty$1(this, "onAdError", event => {
        this.cancel();
        this.player.debug.warn('Ads error', event);
      });
      /**
       * Setup hooks for Plyr and window events. This ensures
       * the mid- and post-roll launch at the correct time. And
       * resize the advertisement when the player resizes
       */
      _defineProperty$1(this, "listeners", () => {
        const {
          container
        } = this.player.elements;
        let time;
        this.player.on('canplay', () => {
          this.addCuePoints();
        });
        this.player.on('ended', () => {
          this.loader.contentComplete();
        });
        this.player.on('timeupdate', () => {
          time = this.player.currentTime;
        });
        this.player.on('seeked', () => {
          const seekedTime = this.player.currentTime;
          if (is.empty(this.cuePoints)) {
            return;
          }
          this.cuePoints.forEach((cuePoint, index) => {
            if (time < cuePoint && cuePoint < seekedTime) {
              this.manager.discardAdBreak();
              this.cuePoints.splice(index, 1);
            }
          });
        });

        // Listen to the resizing of the window. And resize ad accordingly
        // TODO: eventually implement ResizeObserver
        window.addEventListener('resize', () => {
          if (this.manager) {
            this.manager.resize(container.offsetWidth, container.offsetHeight, google.ima.ViewMode.NORMAL);
          }
        });
      });
      /**
       * Initialize the adsManager and start playing advertisements
       */
      _defineProperty$1(this, "play", () => {
        const {
          container
        } = this.player.elements;
        if (!this.managerPromise) {
          this.resumeContent();
        }

        // Play the requested advertisement whenever the adsManager is ready
        this.managerPromise.then(() => {
          // Set volume to match player
          this.manager.setVolume(this.player.volume);

          // Initialize the container. Must be done via a user action on mobile devices
          this.elements.displayContainer.initialize();
          try {
            if (!this.initialized) {
              // Initialize the ads manager. Ad rules playlist will start at this time
              this.manager.init(container.offsetWidth, container.offsetHeight, google.ima.ViewMode.NORMAL);

              // Call play to start showing the ad. Single video and overlay ads will
              // start at this time; the call will be ignored for ad rules
              this.manager.start();
            }
            this.initialized = true;
          } catch (adError) {
            // An error may be thrown if there was a problem with the
            // VAST response
            this.onAdError(adError);
          }
        }).catch(() => {});
      });
      /**
       * Resume our video
       */
      _defineProperty$1(this, "resumeContent", () => {
        // Hide the advertisement container
        this.elements.container.style.zIndex = '';

        // Ad is stopped
        this.playing = false;

        // Play video
        silencePromise(this.player.media.play());
      });
      /**
       * Pause our video
       */
      _defineProperty$1(this, "pauseContent", () => {
        // Show the advertisement container
        this.elements.container.style.zIndex = 3;

        // Ad is playing
        this.playing = true;

        // Pause our video.
        this.player.media.pause();
      });
      /**
       * Destroy the adsManager so we can grab new ads after this. If we don't then we're not
       * allowed to call new ads based on google policies, as they interpret this as an accidental
       * video requests. https://developers.google.com/interactive-
       * media-ads/docs/sdks/android/faq#8
       */
      _defineProperty$1(this, "cancel", () => {
        // Pause our video
        if (this.initialized) {
          this.resumeContent();
        }

        // Tell our instance that we're done for now
        this.trigger('error');

        // Re-create our adsManager
        this.loadAds();
      });
      /**
       * Re-create our adsManager
       */
      _defineProperty$1(this, "loadAds", () => {
        // Tell our adsManager to go bye bye
        this.managerPromise.then(() => {
          // Destroy our adsManager
          if (this.manager) {
            this.manager.destroy();
          }

          // Re-set our adsManager promises
          this.managerPromise = new Promise(resolve => {
            this.on('loaded', resolve);
            this.player.debug.log(this.manager);
          });
          // Now that the manager has been destroyed set it to also be un-initialized
          this.initialized = false;

          // Now request some new advertisements
          this.requestAds();
        }).catch(() => {});
      });
      /**
       * Handles callbacks after an ad event was invoked
       * @param {String} event - Event type
       * @param args
       */
      _defineProperty$1(this, "trigger", (event, ...args) => {
        const handlers = this.events[event];
        if (is.array(handlers)) {
          handlers.forEach(handler => {
            if (is.function(handler)) {
              handler.apply(this, args);
            }
          });
        }
      });
      /**
       * Add event listeners
       * @param {String} event - Event type
       * @param {Function} callback - Callback for when event occurs
       * @return {Ads}
       */
      _defineProperty$1(this, "on", (event, callback) => {
        if (!is.array(this.events[event])) {
          this.events[event] = [];
        }
        this.events[event].push(callback);
        return this;
      });
      /**
       * Setup a safety timer for when the ad network doesn't respond for whatever reason.
       * The advertisement has 12 seconds to get its things together. We stop this timer when the
       * advertisement is playing, or when a user action is required to start, then we clear the
       * timer on ad ready
       * @param {Number} time
       * @param {String} from
       */
      _defineProperty$1(this, "startSafetyTimer", (time, from) => {
        this.player.debug.log(`Safety timer invoked from: ${from}`);
        this.safetyTimer = setTimeout(() => {
          this.cancel();
          this.clearSafetyTimer('startSafetyTimer()');
        }, time);
      });
      /**
       * Clear our safety timer(s)
       * @param {String} from
       */
      _defineProperty$1(this, "clearSafetyTimer", from => {
        if (!is.nullOrUndefined(this.safetyTimer)) {
          this.player.debug.log(`Safety timer cleared from: ${from}`);
          clearTimeout(this.safetyTimer);
          this.safetyTimer = null;
        }
      });
      this.player = player;
      this.config = player.config.ads;
      this.playing = false;
      this.initialized = false;
      this.elements = {
        container: null,
        displayContainer: null
      };
      this.manager = null;
      this.loader = null;
      this.cuePoints = null;
      this.events = {};
      this.safetyTimer = null;
      this.countdownTimer = null;

      // Setup a promise to resolve when the IMA manager is ready
      this.managerPromise = new Promise((resolve, reject) => {
        // The ad is loaded and ready
        this.on('loaded', resolve);

        // Ads failed
        this.on('error', reject);
      });
      this.load();
    }
    get enabled() {
      const {
        config
      } = this;
      return this.player.isHTML5 && this.player.isVideo && config.enabled && (!is.empty(config.publisherId) || is.url(config.tagUrl));
    }
    // Build the tag URL
    get tagUrl() {
      const {
        config
      } = this;
      if (is.url(config.tagUrl)) {
        return config.tagUrl;
      }
      const params = {
        AV_PUBLISHERID: '58c25bb0073ef448b1087ad6',
        AV_CHANNELID: '5a0458dc28a06145e4519d21',
        AV_URL: window.location.hostname,
        cb: Date.now(),
        AV_WIDTH: 640,
        AV_HEIGHT: 480,
        AV_CDIM2: config.publisherId
      };
      const base = 'https://go.aniview.com/api/adserver6/vast/';
      return `${base}?${buildUrlParams(params)}`;
    }
  }

  /**
   * Returns a number whose value is limited to the given range.
   *
   * Example: limit the output of this computation to between 0 and 255
   * (x * 255).clamp(0, 255)
   *
   * @param {Number} input
   * @param {Number} min The lower boundary of the output range
   * @param {Number} max The upper boundary of the output range
   * @returns A number within the bounds of min and max
   * @type Number
   */
  function clamp(input = 0, min = 0, max = 255) {
    return Math.min(Math.max(input, min), max);
  }

  // Arg: vttDataString example: "WEBVTT\n\n1\n00:00:05.000 --> 00:00:10.000\n1080p-00001.jpg"
  const parseVtt = vttDataString => {
    const processedList = [];
    const frames = vttDataString.split(/\r\n\r\n|\n\n|\r\r/);
    frames.forEach(frame => {
      const result = {};
      const lines = frame.split(/\r\n|\n|\r/);
      lines.forEach(line => {
        if (!is.number(result.startTime)) {
          // The line with start and end times on it is the first line of interest
          const matchTimes = line.match(/([0-9]{2})?:?([0-9]{2}):([0-9]{2}).([0-9]{2,3})( ?--> ?)([0-9]{2})?:?([0-9]{2}):([0-9]{2}).([0-9]{2,3})/); // Note that this currently ignores caption formatting directives that are optionally on the end of this line - fine for non-captions VTT

          if (matchTimes) {
            result.startTime = Number(matchTimes[1] || 0) * 60 * 60 + Number(matchTimes[2]) * 60 + Number(matchTimes[3]) + Number(`0.${matchTimes[4]}`);
            result.endTime = Number(matchTimes[6] || 0) * 60 * 60 + Number(matchTimes[7]) * 60 + Number(matchTimes[8]) + Number(`0.${matchTimes[9]}`);
          }
        } else if (!is.empty(line.trim()) && is.empty(result.text)) {
          // If we already have the startTime, then we're definitely up to the text line(s)
          const lineSplit = line.trim().split('#xywh=');
          [result.text] = lineSplit;

          // If there's content in lineSplit[1], then we have sprites. If not, then it's just one frame per image
          if (lineSplit[1]) {
            [result.x, result.y, result.w, result.h] = lineSplit[1].split(',');
          }
        }
      });
      if (result.text) {
        processedList.push(result);
      }
    });
    return processedList;
  };

  /**
   * Preview thumbnails for seek hover and scrubbing
   * Seeking: Hover over the seek bar (desktop only): shows a small preview container above the seek bar
   * Scrubbing: Click and drag the seek bar (desktop and mobile): shows the preview image over the entire video, as if the video is scrubbing at very high speed
   *
   * Notes:
   * - Thumbs are set via JS settings on Plyr init, not HTML5 'track' property. Using the track property would be a bit gross, because it doesn't support custom 'kinds'. kind=metadata might be used for something else, and we want to allow multiple thumbnails tracks. Tracks must have a unique combination of 'kind' and 'label'. We would have to do something like kind=metadata,label=thumbnails1 / kind=metadata,label=thumbnails2. Square peg, round hole
   * - VTT info: the image URL is relative to the VTT, not the current document. But if the url starts with a slash, it will naturally be relative to the current domain. https://support.jwplayer.com/articles/how-to-add-preview-thumbnails
   * - This implementation uses multiple separate img elements. Other implementations use background-image on one element. This would be nice and simple, but Firefox and Safari have flickering issues with replacing backgrounds of larger images. It seems that YouTube perhaps only avoids this because they don't have the option for high-res previews (even the fullscreen ones, when mousedown/seeking). Images appear over the top of each other, and previous ones are discarded once the new ones have been rendered
   */

  const fitRatio = (ratio, outer) => {
    const targetRatio = outer.width / outer.height;
    const result = {};
    if (ratio > targetRatio) {
      result.width = outer.width;
      result.height = 1 / ratio * outer.width;
    } else {
      result.height = outer.height;
      result.width = ratio * outer.height;
    }
    return result;
  };
  class PreviewThumbnails {
    /**
     * PreviewThumbnails constructor.
     * @param {Plyr} player
     * @return {PreviewThumbnails}
     */
    constructor(player) {
      _defineProperty$1(this, "load", () => {
        // Toggle the regular seek tooltip
        if (this.player.elements.display.seekTooltip) {
          this.player.elements.display.seekTooltip.hidden = this.enabled;
        }
        if (!this.enabled) return;
        this.getThumbnails().then(() => {
          if (!this.enabled) {
            return;
          }

          // Render DOM elements
          this.render();

          // Check to see if thumb container size was specified manually in CSS
          this.determineContainerAutoSizing();

          // Set up listeners
          this.listeners();
          this.loaded = true;
        });
      });
      // Download VTT files and parse them
      _defineProperty$1(this, "getThumbnails", () => {
        return new Promise(resolve => {
          const {
            src
          } = this.player.config.previewThumbnails;
          if (is.empty(src)) {
            throw new Error('Missing previewThumbnails.src config attribute');
          }

          // Resolve promise
          const sortAndResolve = () => {
            // Sort smallest to biggest (e.g., [120p, 480p, 1080p])
            this.thumbnails.sort((x, y) => x.height - y.height);
            this.player.debug.log('Preview thumbnails', this.thumbnails);
            resolve();
          };

          // Via callback()
          if (is.function(src)) {
            src(thumbnails => {
              this.thumbnails = thumbnails;
              sortAndResolve();
            });
          }
          // VTT urls
          else {
            // If string, convert into single-element list
            const urls = is.string(src) ? [src] : src;
            // Loop through each src URL. Download and process the VTT file, storing the resulting data in this.thumbnails
            const promises = urls.map(u => this.getThumbnail(u));
            // Resolve
            Promise.all(promises).then(sortAndResolve);
          }
        });
      });
      // Process individual VTT file
      _defineProperty$1(this, "getThumbnail", url => {
        return new Promise(resolve => {
          fetch(url).then(response => {
            const thumbnail = {
              frames: parseVtt(response),
              height: null,
              urlPrefix: ''
            };

            // If the URLs don't start with '/', then we need to set their relative path to be the location of the VTT file
            // If the URLs do start with '/', then they obviously don't need a prefix, so it will remain blank
            // If the thumbnail URLs start with with none of '/', 'http://' or 'https://', then we need to set their relative path to be the location of the VTT file
            if (!thumbnail.frames[0].text.startsWith('/') && !thumbnail.frames[0].text.startsWith('http://') && !thumbnail.frames[0].text.startsWith('https://')) {
              thumbnail.urlPrefix = url.substring(0, url.lastIndexOf('/') + 1);
            }

            // Download the first frame, so that we can determine/set the height of this thumbnailsDef
            const tempImage = new Image();
            tempImage.onload = () => {
              thumbnail.height = tempImage.naturalHeight;
              thumbnail.width = tempImage.naturalWidth;
              this.thumbnails.push(thumbnail);
              resolve();
            };
            tempImage.src = thumbnail.urlPrefix + thumbnail.frames[0].text;
          });
        });
      });
      _defineProperty$1(this, "startMove", event => {
        if (!this.loaded) return;
        if (!is.event(event) || !['touchmove', 'mousemove'].includes(event.type)) return;

        // Wait until media has a duration
        if (!this.player.media.duration) return;
        if (event.type === 'touchmove') {
          // Calculate seek hover position as approx video seconds
          this.seekTime = this.player.media.duration * (this.player.elements.inputs.seek.value / 100);
        } else {
          var _this$player$config$m, _this$player$config$m2;
          // Calculate seek hover position as approx video seconds
          const clientRect = this.player.elements.progress.getBoundingClientRect();
          const percentage = 100 / clientRect.width * (event.pageX - clientRect.left);
          this.seekTime = this.player.media.duration * (percentage / 100);
          if (this.seekTime < 0) {
            // The mousemove fires for 10+px out to the left
            this.seekTime = 0;
          }
          if (this.seekTime > this.player.media.duration - 1) {
            // Took 1 second off the duration for safety, because different players can disagree on the real duration of a video
            this.seekTime = this.player.media.duration - 1;
          }
          this.mousePosX = event.pageX;

          // Set time text inside image container
          this.elements.thumb.time.innerText = formatTime(this.seekTime);

          // Get marker point for time
          const point = (_this$player$config$m = this.player.config.markers) === null || _this$player$config$m === void 0 ? void 0 : (_this$player$config$m2 = _this$player$config$m.points) === null || _this$player$config$m2 === void 0 ? void 0 : _this$player$config$m2.find(({
            time: t
          }) => t === Math.round(this.seekTime));

          // Append the point label to the tooltip
          if (point) {
            // this.elements.thumb.time.innerText.concat('\n');
            this.elements.thumb.time.insertAdjacentHTML('afterbegin', `${point.label}<br>`);
          }
        }

        // Download and show image
        this.showImageAtCurrentTime();
      });
      _defineProperty$1(this, "endMove", () => {
        this.toggleThumbContainer(false, true);
      });
      _defineProperty$1(this, "startScrubbing", event => {
        // Only act on left mouse button (0), or touch device (event.button does not exist or is false)
        if (is.nullOrUndefined(event.button) || event.button === false || event.button === 0) {
          this.mouseDown = true;

          // Wait until media has a duration
          if (this.player.media.duration) {
            this.toggleScrubbingContainer(true);
            this.toggleThumbContainer(false, true);

            // Download and show image
            this.showImageAtCurrentTime();
          }
        }
      });
      _defineProperty$1(this, "endScrubbing", () => {
        this.mouseDown = false;

        // Hide scrubbing preview. But wait until the video has successfully seeked before hiding the scrubbing preview
        if (Math.ceil(this.lastTime) === Math.ceil(this.player.media.currentTime)) {
          // The video was already seeked/loaded at the chosen time - hide immediately
          this.toggleScrubbingContainer(false);
        } else {
          // The video hasn't seeked yet. Wait for that
          once.call(this.player, this.player.media, 'timeupdate', () => {
            // Re-check mousedown - we might have already started scrubbing again
            if (!this.mouseDown) {
              this.toggleScrubbingContainer(false);
            }
          });
        }
      });
      /**
       * Setup hooks for Plyr and window events
       */
      _defineProperty$1(this, "listeners", () => {
        // Hide thumbnail preview - on mouse click, mouse leave (in listeners.js for now), and video play/seek. All four are required, e.g., for buffering
        this.player.on('play', () => {
          this.toggleThumbContainer(false, true);
        });
        this.player.on('seeked', () => {
          this.toggleThumbContainer(false);
        });
        this.player.on('timeupdate', () => {
          this.lastTime = this.player.media.currentTime;
        });
      });
      /**
       * Create HTML elements for image containers
       */
      _defineProperty$1(this, "render", () => {
        // Create HTML element: plyr__preview-thumbnail-container
        this.elements.thumb.container = createElement('div', {
          class: this.player.config.classNames.previewThumbnails.thumbContainer
        });

        // Wrapper for the image for styling
        this.elements.thumb.imageContainer = createElement('div', {
          class: this.player.config.classNames.previewThumbnails.imageContainer
        });
        this.elements.thumb.container.appendChild(this.elements.thumb.imageContainer);

        // Create HTML element, parent+span: time text (e.g., 01:32:00)
        const timeContainer = createElement('div', {
          class: this.player.config.classNames.previewThumbnails.timeContainer
        });
        this.elements.thumb.time = createElement('span', {}, '00:00');
        timeContainer.appendChild(this.elements.thumb.time);
        this.elements.thumb.imageContainer.appendChild(timeContainer);

        // Inject the whole thumb
        if (is.element(this.player.elements.progress)) {
          this.player.elements.progress.appendChild(this.elements.thumb.container);
        }

        // Create HTML element: plyr__preview-scrubbing-container
        this.elements.scrubbing.container = createElement('div', {
          class: this.player.config.classNames.previewThumbnails.scrubbingContainer
        });
        this.player.elements.wrapper.appendChild(this.elements.scrubbing.container);
      });
      _defineProperty$1(this, "destroy", () => {
        if (this.elements.thumb.container) {
          this.elements.thumb.container.remove();
        }
        if (this.elements.scrubbing.container) {
          this.elements.scrubbing.container.remove();
        }
      });
      _defineProperty$1(this, "showImageAtCurrentTime", () => {
        if (this.mouseDown) {
          this.setScrubbingContainerSize();
        } else {
          this.setThumbContainerSizeAndPos();
        }

        // Find the desired thumbnail index
        // TODO: Handle a video longer than the thumbs where thumbNum is null
        const thumbNum = this.thumbnails[0].frames.findIndex(frame => this.seekTime >= frame.startTime && this.seekTime <= frame.endTime);
        const hasThumb = thumbNum >= 0;
        let qualityIndex = 0;

        // Show the thumb container if we're not scrubbing
        if (!this.mouseDown) {
          this.toggleThumbContainer(hasThumb);
        }

        // No matching thumb found
        if (!hasThumb) {
          return;
        }

        // Check to see if we've already downloaded higher quality versions of this image
        this.thumbnails.forEach((thumbnail, index) => {
          if (this.loadedImages.includes(thumbnail.frames[thumbNum].text)) {
            qualityIndex = index;
          }
        });

        // Only proceed if either thumb num or thumbfilename has changed
        if (thumbNum !== this.showingThumb) {
          this.showingThumb = thumbNum;
          this.loadImage(qualityIndex);
        }
      });
      // Show the image that's currently specified in this.showingThumb
      _defineProperty$1(this, "loadImage", (qualityIndex = 0) => {
        const thumbNum = this.showingThumb;
        const thumbnail = this.thumbnails[qualityIndex];
        const {
          urlPrefix
        } = thumbnail;
        const frame = thumbnail.frames[thumbNum];
        const thumbFilename = thumbnail.frames[thumbNum].text;
        const thumbUrl = urlPrefix + thumbFilename;
        if (!this.currentImageElement || this.currentImageElement.dataset.filename !== thumbFilename) {
          // If we're already loading a previous image, remove its onload handler - we don't want it to load after this one
          // Only do this if not using sprites. Without sprites we really want to show as many images as possible, as a best-effort
          if (this.loadingImage && this.usingSprites) {
            this.loadingImage.onload = null;
          }

          // We're building and adding a new image. In other implementations of similar functionality (YouTube), background image
          // is instead used. But this causes issues with larger images in Firefox and Safari - switching between background
          // images causes a flicker. Putting a new image over the top does not
          const previewImage = new Image();
          previewImage.src = thumbUrl;
          previewImage.dataset.index = thumbNum;
          previewImage.dataset.filename = thumbFilename;
          this.showingThumbFilename = thumbFilename;
          this.player.debug.log(`Loading image: ${thumbUrl}`);

          // For some reason, passing the named function directly causes it to execute immediately. So I've wrapped it in an anonymous function...
          previewImage.onload = () => this.showImage(previewImage, frame, qualityIndex, thumbNum, thumbFilename, true);
          this.loadingImage = previewImage;
          this.removeOldImages(previewImage);
        } else {
          // Update the existing image
          this.showImage(this.currentImageElement, frame, qualityIndex, thumbNum, thumbFilename, false);
          this.currentImageElement.dataset.index = thumbNum;
          this.removeOldImages(this.currentImageElement);
        }
      });
      _defineProperty$1(this, "showImage", (previewImage, frame, qualityIndex, thumbNum, thumbFilename, newImage = true) => {
        this.player.debug.log(`Showing thumb: ${thumbFilename}. num: ${thumbNum}. qual: ${qualityIndex}. newimg: ${newImage}`);
        this.setImageSizeAndOffset(previewImage, frame);
        if (newImage) {
          this.currentImageContainer.appendChild(previewImage);
          this.currentImageElement = previewImage;
          if (!this.loadedImages.includes(thumbFilename)) {
            this.loadedImages.push(thumbFilename);
          }
        }

        // Preload images before and after the current one
        // Show higher quality of the same frame
        // Each step here has a short time delay, and only continues if still hovering/seeking the same spot. This is to protect slow connections from overloading
        this.preloadNearby(thumbNum, true).then(this.preloadNearby(thumbNum, false)).then(this.getHigherQuality(qualityIndex, previewImage, frame, thumbFilename));
      });
      // Remove all preview images that aren't the designated current image
      _defineProperty$1(this, "removeOldImages", currentImage => {
        // Get a list of all images, convert it from a DOM list to an array
        Array.from(this.currentImageContainer.children).forEach(image => {
          if (image.tagName.toLowerCase() !== 'img') {
            return;
          }
          const removeDelay = this.usingSprites ? 500 : 1000;
          if (image.dataset.index !== currentImage.dataset.index && !image.dataset.deleting) {
            // Wait 200ms, as the new image can take some time to show on certain browsers (even though it was downloaded before showing). This will prevent flicker, and show some generosity towards slower clients
            // First set attribute 'deleting' to prevent multi-handling of this on repeat firing of this function
            // eslint-disable-next-line no-param-reassign
            image.dataset.deleting = true;

            // This has to be set before the timeout - to prevent issues switching between hover and scrub
            const {
              currentImageContainer
            } = this;
            setTimeout(() => {
              currentImageContainer.removeChild(image);
              this.player.debug.log(`Removing thumb: ${image.dataset.filename}`);
            }, removeDelay);
          }
        });
      });
      // Preload images before and after the current one. Only if the user is still hovering/seeking the same frame
      // This will only preload the lowest quality
      _defineProperty$1(this, "preloadNearby", (thumbNum, forward = true) => {
        return new Promise(resolve => {
          setTimeout(() => {
            const oldThumbFilename = this.thumbnails[0].frames[thumbNum].text;
            if (this.showingThumbFilename === oldThumbFilename) {
              // Find the nearest thumbs with different filenames. Sometimes it'll be the next index, but in the case of sprites, it might be 100+ away
              let thumbnailsClone;
              if (forward) {
                thumbnailsClone = this.thumbnails[0].frames.slice(thumbNum);
              } else {
                thumbnailsClone = this.thumbnails[0].frames.slice(0, thumbNum).reverse();
              }
              let foundOne = false;
              thumbnailsClone.forEach(frame => {
                const newThumbFilename = frame.text;
                if (newThumbFilename !== oldThumbFilename) {
                  // Found one with a different filename. Make sure it hasn't already been loaded on this page visit
                  if (!this.loadedImages.includes(newThumbFilename)) {
                    foundOne = true;
                    this.player.debug.log(`Preloading thumb filename: ${newThumbFilename}`);
                    const {
                      urlPrefix
                    } = this.thumbnails[0];
                    const thumbURL = urlPrefix + newThumbFilename;
                    const previewImage = new Image();
                    previewImage.src = thumbURL;
                    previewImage.onload = () => {
                      this.player.debug.log(`Preloaded thumb filename: ${newThumbFilename}`);
                      if (!this.loadedImages.includes(newThumbFilename)) this.loadedImages.push(newThumbFilename);

                      // We don't resolve until the thumb is loaded
                      resolve();
                    };
                  }
                }
              });

              // If there are none to preload then we want to resolve immediately
              if (!foundOne) {
                resolve();
              }
            }
          }, 300);
        });
      });
      // If user has been hovering current image for half a second, look for a higher quality one
      _defineProperty$1(this, "getHigherQuality", (currentQualityIndex, previewImage, frame, thumbFilename) => {
        if (currentQualityIndex < this.thumbnails.length - 1) {
          // Only use the higher quality version if it's going to look any better - if the current thumb is of a lower pixel density than the thumbnail container
          let previewImageHeight = previewImage.naturalHeight;
          if (this.usingSprites) {
            previewImageHeight = frame.h;
          }
          if (previewImageHeight < this.thumbContainerHeight) {
            // Recurse back to the loadImage function - show a higher quality one, but only if the viewer is on this frame for a while
            setTimeout(() => {
              // Make sure the mouse hasn't already moved on and started hovering at another image
              if (this.showingThumbFilename === thumbFilename) {
                this.player.debug.log(`Showing higher quality thumb for: ${thumbFilename}`);
                this.loadImage(currentQualityIndex + 1);
              }
            }, 300);
          }
        }
      });
      _defineProperty$1(this, "toggleThumbContainer", (toggle = false, clearShowing = false) => {
        const className = this.player.config.classNames.previewThumbnails.thumbContainerShown;
        this.elements.thumb.container.classList.toggle(className, toggle);
        if (!toggle && clearShowing) {
          this.showingThumb = null;
          this.showingThumbFilename = null;
        }
      });
      _defineProperty$1(this, "toggleScrubbingContainer", (toggle = false) => {
        const className = this.player.config.classNames.previewThumbnails.scrubbingContainerShown;
        this.elements.scrubbing.container.classList.toggle(className, toggle);
        if (!toggle) {
          this.showingThumb = null;
          this.showingThumbFilename = null;
        }
      });
      _defineProperty$1(this, "determineContainerAutoSizing", () => {
        if (this.elements.thumb.imageContainer.clientHeight > 20 || this.elements.thumb.imageContainer.clientWidth > 20) {
          // This will prevent auto sizing in this.setThumbContainerSizeAndPos()
          this.sizeSpecifiedInCSS = true;
        }
      });
      // Set the size to be about a quarter of the size of video. Unless option dynamicSize === false, in which case it needs to be set in CSS
      _defineProperty$1(this, "setThumbContainerSizeAndPos", () => {
        const {
          imageContainer
        } = this.elements.thumb;
        if (!this.sizeSpecifiedInCSS) {
          const thumbWidth = Math.floor(this.thumbContainerHeight * this.thumbAspectRatio);
          imageContainer.style.height = `${this.thumbContainerHeight}px`;
          imageContainer.style.width = `${thumbWidth}px`;
        } else if (imageContainer.clientHeight > 20 && imageContainer.clientWidth < 20) {
          const thumbWidth = Math.floor(imageContainer.clientHeight * this.thumbAspectRatio);
          imageContainer.style.width = `${thumbWidth}px`;
        } else if (imageContainer.clientHeight < 20 && imageContainer.clientWidth > 20) {
          const thumbHeight = Math.floor(imageContainer.clientWidth / this.thumbAspectRatio);
          imageContainer.style.height = `${thumbHeight}px`;
        }
        this.setThumbContainerPos();
      });
      _defineProperty$1(this, "setThumbContainerPos", () => {
        const scrubberRect = this.player.elements.progress.getBoundingClientRect();
        const containerRect = this.player.elements.container.getBoundingClientRect();
        const {
          container
        } = this.elements.thumb;
        // Find the lowest and highest desired left-position, so we don't slide out the side of the video container
        const min = containerRect.left - scrubberRect.left + 10;
        const max = containerRect.right - scrubberRect.left - container.clientWidth - 10;
        // Set preview container position to: mousepos, minus seekbar.left, minus half of previewContainer.clientWidth
        const position = this.mousePosX - scrubberRect.left - container.clientWidth / 2;
        const clamped = clamp(position, min, max);

        // Move the popover position
        container.style.left = `${clamped}px`;

        // The arrow can follow the cursor
        container.style.setProperty('--preview-arrow-offset', `${position - clamped}px`);
      });
      // Can't use 100% width, in case the video is a different aspect ratio to the video container
      _defineProperty$1(this, "setScrubbingContainerSize", () => {
        const {
          width,
          height
        } = fitRatio(this.thumbAspectRatio, {
          width: this.player.media.clientWidth,
          height: this.player.media.clientHeight
        });
        this.elements.scrubbing.container.style.width = `${width}px`;
        this.elements.scrubbing.container.style.height = `${height}px`;
      });
      // Sprites need to be offset to the correct location
      _defineProperty$1(this, "setImageSizeAndOffset", (previewImage, frame) => {
        if (!this.usingSprites) return;

        // Find difference between height and preview container height
        const multiplier = this.thumbContainerHeight / frame.h;

        // eslint-disable-next-line no-param-reassign
        previewImage.style.height = `${previewImage.naturalHeight * multiplier}px`;
        // eslint-disable-next-line no-param-reassign
        previewImage.style.width = `${previewImage.naturalWidth * multiplier}px`;
        // eslint-disable-next-line no-param-reassign
        previewImage.style.left = `-${frame.x * multiplier}px`;
        // eslint-disable-next-line no-param-reassign
        previewImage.style.top = `-${frame.y * multiplier}px`;
      });
      this.player = player;
      this.thumbnails = [];
      this.loaded = false;
      this.lastMouseMoveTime = Date.now();
      this.mouseDown = false;
      this.loadedImages = [];
      this.elements = {
        thumb: {},
        scrubbing: {}
      };
      this.load();
    }
    get enabled() {
      return this.player.isHTML5 && this.player.isVideo && this.player.config.previewThumbnails.enabled;
    }
    get currentImageContainer() {
      return this.mouseDown ? this.elements.scrubbing.container : this.elements.thumb.imageContainer;
    }
    get usingSprites() {
      return Object.keys(this.thumbnails[0].frames[0]).includes('w');
    }
    get thumbAspectRatio() {
      if (this.usingSprites) {
        return this.thumbnails[0].frames[0].w / this.thumbnails[0].frames[0].h;
      }
      return this.thumbnails[0].width / this.thumbnails[0].height;
    }
    get thumbContainerHeight() {
      if (this.mouseDown) {
        const {
          height
        } = fitRatio(this.thumbAspectRatio, {
          width: this.player.media.clientWidth,
          height: this.player.media.clientHeight
        });
        return height;
      }

      // If css is used this needs to return the css height for sprites to work (see setImageSizeAndOffset)
      if (this.sizeSpecifiedInCSS) {
        return this.elements.thumb.imageContainer.clientHeight;
      }
      return Math.floor(this.player.media.clientWidth / this.thumbAspectRatio / 4);
    }
    get currentImageElement() {
      return this.mouseDown ? this.currentScrubbingImageElement : this.currentThumbnailImageElement;
    }
    set currentImageElement(element) {
      if (this.mouseDown) {
        this.currentScrubbingImageElement = element;
      } else {
        this.currentThumbnailImageElement = element;
      }
    }
  }

  // ==========================================================================
  const source = {
    // Add elements to HTML5 media (source, tracks, etc)
    insertElements(type, attributes) {
      if (is.string(attributes)) {
        insertElement(type, this.media, {
          src: attributes
        });
      } else if (is.array(attributes)) {
        attributes.forEach(attribute => {
          insertElement(type, this.media, attribute);
        });
      }
    },
    // Update source
    // Sources are not checked for support so be careful
    change(input) {
      if (!getDeep(input, 'sources.length')) {
        this.debug.warn('Invalid source format');
        return;
      }

      // Cancel current network requests
      html5.cancelRequests.call(this);

      // Destroy instance and re-setup
      this.destroy.call(this, () => {
        // Reset quality options
        this.options.quality = [];

        // Remove elements
        removeElement(this.media);
        this.media = null;

        // Reset class name
        if (is.element(this.elements.container)) {
          this.elements.container.removeAttribute('class');
        }

        // Set the type and provider
        const {
          sources,
          type
        } = input;
        const [{
          provider = providers.html5,
          src
        }] = sources;
        const tagName = provider === 'html5' ? type : 'div';
        const attributes = provider === 'html5' ? {} : {
          src
        };
        Object.assign(this, {
          provider,
          type,
          // Check for support
          supported: support.check(type, provider, this.config.playsinline),
          // Create new element
          media: createElement(tagName, attributes)
        });

        // Inject the new element
        this.elements.container.appendChild(this.media);

        // Autoplay the new source?
        if (is.boolean(input.autoplay)) {
          this.config.autoplay = input.autoplay;
        }

        // Set attributes for audio and video
        if (this.isHTML5) {
          if (this.config.crossorigin) {
            this.media.setAttribute('crossorigin', '');
          }
          if (this.config.autoplay) {
            this.media.setAttribute('autoplay', '');
          }
          if (!is.empty(input.poster)) {
            this.poster = input.poster;
          }
          if (this.config.loop.active) {
            this.media.setAttribute('loop', '');
          }
          if (this.config.muted) {
            this.media.setAttribute('muted', '');
          }
          if (this.config.playsinline) {
            this.media.setAttribute('playsinline', '');
          }
        }

        // Restore class hook
        ui.addStyleHook.call(this);

        // Set new sources for html5
        if (this.isHTML5) {
          source.insertElements.call(this, 'source', sources);
        }

        // Set video title
        this.config.title = input.title;

        // Set up from scratch
        media.setup.call(this);

        // HTML5 stuff
        if (this.isHTML5) {
          // Setup captions
          if (Object.keys(input).includes('tracks')) {
            source.insertElements.call(this, 'track', input.tracks);
          }
        }

        // If HTML5 or embed but not fully supported, setupInterface and call ready now
        if (this.isHTML5 || this.isEmbed && !this.supported.ui) {
          // Setup interface
          ui.build.call(this);
        }

        // Load HTML5 sources
        if (this.isHTML5) {
          this.media.load();
        }

        // Update previewThumbnails config & reload plugin
        if (!is.empty(input.previewThumbnails)) {
          Object.assign(this.config.previewThumbnails, input.previewThumbnails);

          // Cleanup previewThumbnails plugin if it was loaded
          if (this.previewThumbnails && this.previewThumbnails.loaded) {
            this.previewThumbnails.destroy();
            this.previewThumbnails = null;
          }

          // Create new instance if it is still enabled
          if (this.config.previewThumbnails.enabled) {
            this.previewThumbnails = new PreviewThumbnails(this);
          }
        }

        // Update the fullscreen support
        this.fullscreen.update();
      }, true);
    }
  };

  // Private properties
  // TODO: Use a WeakMap for private globals
  // const globals = new WeakMap();

  // Plyr instance
  class Plyr {
    constructor(target, options) {
      /**
       * Play the media, or play the advertisement (if they are not blocked)
       */
      _defineProperty$1(this, "play", () => {
        if (!is.function(this.media.play)) {
          return null;
        }

        // Intecept play with ads
        if (this.ads && this.ads.enabled) {
          this.ads.managerPromise.then(() => this.ads.play()).catch(() => silencePromise(this.media.play()));
        }

        // Return the promise (for HTML5)
        return this.media.play();
      });
      /**
       * Pause the media
       */
      _defineProperty$1(this, "pause", () => {
        if (!this.playing || !is.function(this.media.pause)) {
          return null;
        }
        return this.media.pause();
      });
      /**
       * Toggle playback based on current status
       * @param {Boolean} input
       */
      _defineProperty$1(this, "togglePlay", input => {
        // Toggle based on current state if nothing passed
        const toggle = is.boolean(input) ? input : !this.playing;
        if (toggle) {
          return this.play();
        }
        return this.pause();
      });
      /**
       * Stop playback
       */
      _defineProperty$1(this, "stop", () => {
        if (this.isHTML5) {
          this.pause();
          this.restart();
        } else if (is.function(this.media.stop)) {
          this.media.stop();
        }
      });
      /**
       * Restart playback
       */
      _defineProperty$1(this, "restart", () => {
        this.currentTime = 0;
      });
      /**
       * Rewind
       * @param {Number} seekTime - how far to rewind in seconds. Defaults to the config.seekTime
       */
      _defineProperty$1(this, "rewind", seekTime => {
        this.currentTime -= is.number(seekTime) ? seekTime : this.config.seekTime;
      });
      /**
       * Fast forward
       * @param {Number} seekTime - how far to fast forward in seconds. Defaults to the config.seekTime
       */
      _defineProperty$1(this, "forward", seekTime => {
        this.currentTime += is.number(seekTime) ? seekTime : this.config.seekTime;
      });
      /**
       * Increase volume
       * @param {Boolean} step - How much to decrease by (between 0 and 1)
       */
      _defineProperty$1(this, "increaseVolume", step => {
        const volume = this.media.muted ? 0 : this.volume;
        this.volume = volume + (is.number(step) ? step : 0);
      });
      /**
       * Decrease volume
       * @param {Boolean} step - How much to decrease by (between 0 and 1)
       */
      _defineProperty$1(this, "decreaseVolume", step => {
        this.increaseVolume(-step);
      });
      /**
       * Trigger the airplay dialog
       * TODO: update player with state, support, enabled
       */
      _defineProperty$1(this, "airplay", () => {
        // Show dialog if supported
        if (support.airplay) {
          this.media.webkitShowPlaybackTargetPicker();
        }
      });
      /**
       * Toggle the player controls
       * @param {Boolean} [toggle] - Whether to show the controls
       */
      _defineProperty$1(this, "toggleControls", toggle => {
        // Don't toggle if missing UI support or if it's audio
        if (this.supported.ui && !this.isAudio) {
          // Get state before change
          const isHidden = hasClass(this.elements.container, this.config.classNames.hideControls);
          // Negate the argument if not undefined since adding the class to hides the controls
          const force = typeof toggle === 'undefined' ? undefined : !toggle;
          // Apply and get updated state
          const hiding = toggleClass(this.elements.container, this.config.classNames.hideControls, force);

          // Close menu
          if (hiding && is.array(this.config.controls) && this.config.controls.includes('settings') && !is.empty(this.config.settings)) {
            controls.toggleMenu.call(this, false);
          }

          // Trigger event on change
          if (hiding !== isHidden) {
            const eventName = hiding ? 'controlshidden' : 'controlsshown';
            triggerEvent.call(this, this.media, eventName);
          }
          return !hiding;
        }
        return false;
      });
      /**
       * Add event listeners
       * @param {String} event - Event type
       * @param {Function} callback - Callback for when event occurs
       */
      _defineProperty$1(this, "on", (event, callback) => {
        on.call(this, this.elements.container, event, callback);
      });
      /**
       * Add event listeners once
       * @param {String} event - Event type
       * @param {Function} callback - Callback for when event occurs
       */
      _defineProperty$1(this, "once", (event, callback) => {
        once.call(this, this.elements.container, event, callback);
      });
      /**
       * Remove event listeners
       * @param {String} event - Event type
       * @param {Function} callback - Callback for when event occurs
       */
      _defineProperty$1(this, "off", (event, callback) => {
        off(this.elements.container, event, callback);
      });
      /**
       * Destroy an instance
       * Event listeners are removed when elements are removed
       * http://stackoverflow.com/questions/12528049/if-a-dom-element-is-removed-are-its-listeners-also-removed-from-memory
       * @param {Function} callback - Callback for when destroy is complete
       * @param {Boolean} soft - Whether it's a soft destroy (for source changes etc)
       */
      _defineProperty$1(this, "destroy", (callback, soft = false) => {
        if (!this.ready) {
          return;
        }
        const done = () => {
          // Reset overflow (incase destroyed while in fullscreen)
          document.body.style.overflow = '';

          // GC for embed
          this.embed = null;

          // If it's a soft destroy, make minimal changes
          if (soft) {
            if (Object.keys(this.elements).length) {
              // Remove elements
              removeElement(this.elements.buttons.play);
              removeElement(this.elements.captions);
              removeElement(this.elements.controls);
              removeElement(this.elements.wrapper);

              // Clear for GC
              this.elements.buttons.play = null;
              this.elements.captions = null;
              this.elements.controls = null;
              this.elements.wrapper = null;
            }

            // Callback
            if (is.function(callback)) {
              callback();
            }
          } else {
            // Unbind listeners
            unbindListeners.call(this);

            // Cancel current network requests
            html5.cancelRequests.call(this);

            // Replace the container with the original element provided
            replaceElement(this.elements.original, this.elements.container);

            // Event
            triggerEvent.call(this, this.elements.original, 'destroyed', true);

            // Callback
            if (is.function(callback)) {
              callback.call(this.elements.original);
            }

            // Reset state
            this.ready = false;

            // Clear for garbage collection
            setTimeout(() => {
              this.elements = null;
              this.media = null;
            }, 200);
          }
        };

        // Stop playback
        this.stop();

        // Clear timeouts
        clearTimeout(this.timers.loading);
        clearTimeout(this.timers.controls);
        clearTimeout(this.timers.resized);

        // Provider specific stuff
        if (this.isHTML5) {
          // Restore native video controls
          ui.toggleNativeControls.call(this, true);

          // Clean up
          done();
        } else if (this.isYouTube) {
          // Clear timers
          clearInterval(this.timers.buffering);
          clearInterval(this.timers.playing);

          // Destroy YouTube API
          if (this.embed !== null && is.function(this.embed.destroy)) {
            this.embed.destroy();
          }

          // Clean up
          done();
        } else if (this.isVimeo) {
          // Destroy Vimeo API
          // then clean up (wait, to prevent postmessage errors)
          if (this.embed !== null) {
            this.embed.unload().then(done);
          }

          // Vimeo does not always return
          setTimeout(done, 200);
        }
      });
      /**
       * Check for support for a mime type (HTML5 only)
       * @param {String} type - Mime type
       */
      _defineProperty$1(this, "supports", type => support.mime.call(this, type));
      this.timers = {};

      // State
      this.ready = false;
      this.loading = false;
      this.failed = false;

      // Touch device
      this.touch = support.touch;

      // Set the media element
      this.media = target;

      // String selector passed
      if (is.string(this.media)) {
        this.media = document.querySelectorAll(this.media);
      }

      // jQuery, NodeList or Array passed, use first element
      if (window.jQuery && this.media instanceof jQuery || is.nodeList(this.media) || is.array(this.media)) {
        // eslint-disable-next-line
        this.media = this.media[0];
      }

      // Set config
      this.config = extend({}, defaults, Plyr.defaults, options || {}, (() => {
        try {
          return JSON.parse(this.media.getAttribute('data-plyr-config'));
        } catch (_) {
          return {};
        }
      })());

      // Elements cache
      this.elements = {
        container: null,
        fullscreen: null,
        captions: null,
        buttons: {},
        display: {},
        progress: {},
        inputs: {},
        settings: {
          popup: null,
          menu: null,
          panels: {},
          buttons: {}
        }
      };

      // Captions
      this.captions = {
        active: null,
        currentTrack: -1,
        meta: new WeakMap()
      };

      // Fullscreen
      this.fullscreen = {
        active: false
      };

      // Options
      this.options = {
        speed: [],
        quality: []
      };

      // Debugging
      // TODO: move to globals
      this.debug = new Console(this.config.debug);

      // Log config options and support
      this.debug.log('Config', this.config);
      this.debug.log('Support', support);

      // We need an element to setup
      if (is.nullOrUndefined(this.media) || !is.element(this.media)) {
        this.debug.error('Setup failed: no suitable element passed');
        return;
      }

      // Bail if the element is initialized
      if (this.media.plyr) {
        this.debug.warn('Target already setup');
        return;
      }

      // Bail if not enabled
      if (!this.config.enabled) {
        this.debug.error('Setup failed: disabled by config');
        return;
      }

      // Bail if disabled or no basic support
      // You may want to disable certain UAs etc
      if (!support.check().api) {
        this.debug.error('Setup failed: no support');
        return;
      }

      // Cache original element state for .destroy()
      const clone = this.media.cloneNode(true);
      clone.autoplay = false;
      this.elements.original = clone;

      // Set media type based on tag or data attribute
      // Supported: video, audio, vimeo, youtube
      const _type = this.media.tagName.toLowerCase();
      // Embed properties
      let iframe = null;
      let url = null;

      // Different setup based on type
      switch (_type) {
        case 'div':
          // Find the frame
          iframe = this.media.querySelector('iframe');

          // <iframe> type
          if (is.element(iframe)) {
            // Detect provider
            url = parseUrl(iframe.getAttribute('src'));
            this.provider = getProviderByUrl(url.toString());

            // Rework elements
            this.elements.container = this.media;
            this.media = iframe;

            // Reset classname
            this.elements.container.className = '';

            // Get attributes from URL and set config
            if (url.search.length) {
              const truthy = ['1', 'true'];
              if (truthy.includes(url.searchParams.get('autoplay'))) {
                this.config.autoplay = true;
              }
              if (truthy.includes(url.searchParams.get('loop'))) {
                this.config.loop.active = true;
              }

              // TODO: replace fullscreen.iosNative with this playsinline config option
              // YouTube requires the playsinline in the URL
              if (this.isYouTube) {
                this.config.playsinline = truthy.includes(url.searchParams.get('playsinline'));
                this.config.youtube.hl = url.searchParams.get('hl'); // TODO: Should this be setting language?
              } else {
                this.config.playsinline = true;
              }
            }
          } else {
            // <div> with attributes
            this.provider = this.media.getAttribute(this.config.attributes.embed.provider);

            // Remove attribute
            this.media.removeAttribute(this.config.attributes.embed.provider);
          }

          // Unsupported or missing provider
          if (is.empty(this.provider) || !Object.values(providers).includes(this.provider)) {
            this.debug.error('Setup failed: Invalid provider');
            return;
          }

          // Audio will come later for external providers
          this.type = types.video;
          break;
        case 'video':
        case 'audio':
          this.type = _type;
          this.provider = providers.html5;

          // Get config from attributes
          if (this.media.hasAttribute('crossorigin')) {
            this.config.crossorigin = true;
          }
          if (this.media.hasAttribute('autoplay')) {
            this.config.autoplay = true;
          }
          if (this.media.hasAttribute('playsinline') || this.media.hasAttribute('webkit-playsinline')) {
            this.config.playsinline = true;
          }
          if (this.media.hasAttribute('muted')) {
            this.config.muted = true;
          }
          if (this.media.hasAttribute('loop')) {
            this.config.loop.active = true;
          }
          break;
        default:
          this.debug.error('Setup failed: unsupported type');
          return;
      }

      // Check for support again but with type
      this.supported = support.check(this.type, this.provider);

      // If no support for even API, bail
      if (!this.supported.api) {
        this.debug.error('Setup failed: no support');
        return;
      }
      this.eventListeners = [];

      // Create listeners
      this.listeners = new Listeners(this);

      // Setup local storage for user settings
      this.storage = new Storage(this);

      // Store reference
      this.media.plyr = this;

      // Wrap media
      if (!is.element(this.elements.container)) {
        this.elements.container = createElement('div');
        wrap(this.media, this.elements.container);
      }

      // Migrate custom properties from media to container (so they work 😉)
      ui.migrateStyles.call(this);

      // Add style hook
      ui.addStyleHook.call(this);

      // Setup media
      media.setup.call(this);

      // Listen for events if debugging
      if (this.config.debug) {
        on.call(this, this.elements.container, this.config.events.join(' '), event => {
          this.debug.log(`event: ${event.type}`);
        });
      }

      // Setup fullscreen
      this.fullscreen = new Fullscreen(this);

      // Setup interface
      // If embed but not fully supported, build interface now to avoid flash of controls
      if (this.isHTML5 || this.isEmbed && !this.supported.ui) {
        ui.build.call(this);
      }

      // Container listeners
      this.listeners.container();

      // Global listeners
      this.listeners.global();

      // Setup ads if provided
      if (this.config.ads.enabled) {
        this.ads = new Ads(this);
      }

      // Autoplay if required
      if (this.isHTML5 && this.config.autoplay) {
        this.once('canplay', () => silencePromise(this.play()));
      }

      // Seek time will be recorded (in listeners.js) so we can prevent hiding controls for a few seconds after seek
      this.lastSeekTime = 0;

      // Setup preview thumbnails if enabled
      if (this.config.previewThumbnails.enabled) {
        this.previewThumbnails = new PreviewThumbnails(this);
      }
    }

    // ---------------------------------------
    // API
    // ---------------------------------------

    /**
     * Types and provider helpers
     */
    get isHTML5() {
      return this.provider === providers.html5;
    }
    get isEmbed() {
      return this.isYouTube || this.isVimeo;
    }
    get isYouTube() {
      return this.provider === providers.youtube;
    }
    get isVimeo() {
      return this.provider === providers.vimeo;
    }
    get isVideo() {
      return this.type === types.video;
    }
    get isAudio() {
      return this.type === types.audio;
    }
    /**
     * Get playing state
     */
    get playing() {
      return Boolean(this.ready && !this.paused && !this.ended);
    }

    /**
     * Get paused state
     */
    get paused() {
      return Boolean(this.media.paused);
    }

    /**
     * Get stopped state
     */
    get stopped() {
      return Boolean(this.paused && this.currentTime === 0);
    }

    /**
     * Get ended state
     */
    get ended() {
      return Boolean(this.media.ended);
    }
    /**
     * Seek to a time
     * @param {Number} input - where to seek to in seconds. Defaults to 0 (the start)
     */
    set currentTime(input) {
      // Bail if media duration isn't available yet
      if (!this.duration) {
        return;
      }

      // Validate input
      const inputIsValid = is.number(input) && input > 0;

      // Set
      this.media.currentTime = inputIsValid ? Math.min(input, this.duration) : 0;

      // Logging
      this.debug.log(`Seeking to ${this.currentTime} seconds`);
    }

    /**
     * Get current time
     */
    get currentTime() {
      return Number(this.media.currentTime);
    }

    /**
     * Get buffered
     */
    get buffered() {
      const {
        buffered
      } = this.media;

      // YouTube / Vimeo return a float between 0-1
      if (is.number(buffered)) {
        return buffered;
      }

      // HTML5
      // TODO: Handle buffered chunks of the media
      // (i.e. seek to another section buffers only that section)
      if (buffered && buffered.length && this.duration > 0) {
        return buffered.end(0) / this.duration;
      }
      return 0;
    }

    /**
     * Get seeking status
     */
    get seeking() {
      return Boolean(this.media.seeking);
    }

    /**
     * Get the duration of the current media
     */
    get duration() {
      // Faux duration set via config
      const fauxDuration = parseFloat(this.config.duration);
      // Media duration can be NaN or Infinity before the media has loaded
      const realDuration = (this.media || {}).duration;
      const duration = !is.number(realDuration) || realDuration === Infinity ? 0 : realDuration;

      // If config duration is funky, use regular duration
      return fauxDuration || duration;
    }

    /**
     * Set the player volume
     * @param {Number} value - must be between 0 and 1. Defaults to the value from local storage and config.volume if not set in storage
     */
    set volume(value) {
      let volume = value;
      const max = 1;
      const min = 0;
      if (is.string(volume)) {
        volume = Number(volume);
      }

      // Load volume from storage if no value specified
      if (!is.number(volume)) {
        volume = this.storage.get('volume');
      }

      // Use config if all else fails
      if (!is.number(volume)) {
        ({
          volume
        } = this.config);
      }

      // Maximum is volumeMax
      if (volume > max) {
        volume = max;
      }
      // Minimum is volumeMin
      if (volume < min) {
        volume = min;
      }

      // Update config
      this.config.volume = volume;

      // Set the player volume
      this.media.volume = volume;

      // If muted, and we're increasing volume manually, reset muted state
      if (!is.empty(value) && this.muted && volume > 0) {
        this.muted = false;
      }
    }

    /**
     * Get the current player volume
     */
    get volume() {
      return Number(this.media.volume);
    }
    /**
     * Set muted state
     * @param {Boolean} mute
     */
    set muted(mute) {
      let toggle = mute;

      // Load muted state from storage
      if (!is.boolean(toggle)) {
        toggle = this.storage.get('muted');
      }

      // Use config if all else fails
      if (!is.boolean(toggle)) {
        toggle = this.config.muted;
      }

      // Update config
      this.config.muted = toggle;

      // Set mute on the player
      this.media.muted = toggle;
    }

    /**
     * Get current muted state
     */
    get muted() {
      return Boolean(this.media.muted);
    }

    /**
     * Check if the media has audio
     */
    get hasAudio() {
      // Assume yes for all non HTML5 (as we can't tell...)
      if (!this.isHTML5) {
        return true;
      }
      if (this.isAudio) {
        return true;
      }

      // Get audio tracks
      return Boolean(this.media.mozHasAudio) || Boolean(this.media.webkitAudioDecodedByteCount) || Boolean(this.media.audioTracks && this.media.audioTracks.length);
    }

    /**
     * Set playback speed
     * @param {Number} input - the speed of playback (0.5-2.0)
     */
    set speed(input) {
      let speed = null;
      if (is.number(input)) {
        speed = input;
      }
      if (!is.number(speed)) {
        speed = this.storage.get('speed');
      }
      if (!is.number(speed)) {
        speed = this.config.speed.selected;
      }

      // Clamp to min/max
      const {
        minimumSpeed: min,
        maximumSpeed: max
      } = this;
      speed = clamp(speed, min, max);

      // Update config
      this.config.speed.selected = speed;

      // Set media speed
      setTimeout(() => {
        if (this.media) {
          this.media.playbackRate = speed;
        }
      }, 0);
    }

    /**
     * Get current playback speed
     */
    get speed() {
      return Number(this.media.playbackRate);
    }

    /**
     * Get the minimum allowed speed
     */
    get minimumSpeed() {
      if (this.isYouTube) {
        // https://developers.google.com/youtube/iframe_api_reference#setPlaybackRate
        return Math.min(...this.options.speed);
      }
      if (this.isVimeo) {
        // https://github.com/vimeo/player.js/#setplaybackrateplaybackrate-number-promisenumber-rangeerrorerror
        return 0.5;
      }

      // https://stackoverflow.com/a/32320020/1191319
      return 0.0625;
    }

    /**
     * Get the maximum allowed speed
     */
    get maximumSpeed() {
      if (this.isYouTube) {
        // https://developers.google.com/youtube/iframe_api_reference#setPlaybackRate
        return Math.max(...this.options.speed);
      }
      if (this.isVimeo) {
        // https://github.com/vimeo/player.js/#setplaybackrateplaybackrate-number-promisenumber-rangeerrorerror
        return 2;
      }

      // https://stackoverflow.com/a/32320020/1191319
      return 16;
    }

    /**
     * Set playback quality
     * Currently HTML5 & YouTube only
     * @param {Number} input - Quality level
     */
    set quality(input) {
      const config = this.config.quality;
      const options = this.options.quality;
      if (!options.length) {
        return;
      }
      let quality = [!is.empty(input) && Number(input), this.storage.get('quality'), config.selected, config.default].find(is.number);
      let updateStorage = true;
      if (!options.includes(quality)) {
        const value = closest(options, quality);
        this.debug.warn(`Unsupported quality option: ${quality}, using ${value} instead`);
        quality = value;

        // Don't update storage if quality is not supported
        updateStorage = false;
      }

      // Update config
      config.selected = quality;

      // Set quality
      this.media.quality = quality;

      // Save to storage
      if (updateStorage) {
        this.storage.set({
          quality
        });
      }
    }

    /**
     * Get current quality level
     */
    get quality() {
      return this.media.quality;
    }

    /**
     * Toggle loop
     * TODO: Finish fancy new logic. Set the indicator on load as user may pass loop as config
     * @param {Boolean} input - Whether to loop or not
     */
    set loop(input) {
      const toggle = is.boolean(input) ? input : this.config.loop.active;
      this.config.loop.active = toggle;
      this.media.loop = toggle;

      // Set default to be a true toggle
      /* const type = ['start', 'end', 'all', 'none', 'toggle'].includes(input) ? input : 'toggle';
           switch (type) {
              case 'start':
                  if (this.config.loop.end && this.config.loop.end <= this.currentTime) {
                      this.config.loop.end = null;
                  }
                  this.config.loop.start = this.currentTime;
                  // this.config.loop.indicator.start = this.elements.display.played.value;
                  break;
               case 'end':
                  if (this.config.loop.start >= this.currentTime) {
                      return this;
                  }
                  this.config.loop.end = this.currentTime;
                  // this.config.loop.indicator.end = this.elements.display.played.value;
                  break;
               case 'all':
                  this.config.loop.start = 0;
                  this.config.loop.end = this.duration - 2;
                  this.config.loop.indicator.start = 0;
                  this.config.loop.indicator.end = 100;
                  break;
               case 'toggle':
                  if (this.config.loop.active) {
                      this.config.loop.start = 0;
                      this.config.loop.end = null;
                  } else {
                      this.config.loop.start = 0;
                      this.config.loop.end = this.duration - 2;
                  }
                  break;
               default:
                  this.config.loop.start = 0;
                  this.config.loop.end = null;
                  break;
          } */
    }

    /**
     * Get current loop state
     */
    get loop() {
      return Boolean(this.media.loop);
    }

    /**
     * Set new media source
     * @param {Object} input - The new source object (see docs)
     */
    set source(input) {
      source.change.call(this, input);
    }

    /**
     * Get current source
     */
    get source() {
      return this.media.currentSrc;
    }

    /**
     * Get a download URL (either source or custom)
     */
    get download() {
      const {
        download
      } = this.config.urls;
      return is.url(download) ? download : this.source;
    }

    /**
     * Set the download URL
     */
    set download(input) {
      if (!is.url(input)) {
        return;
      }
      this.config.urls.download = input;
      controls.setDownloadUrl.call(this);
    }

    /**
     * Set the poster image for a video
     * @param {String} input - the URL for the new poster image
     */
    set poster(input) {
      if (!this.isVideo) {
        this.debug.warn('Poster can only be set for video');
        return;
      }
      ui.setPoster.call(this, input, false).catch(() => {});
    }

    /**
     * Get the current poster image
     */
    get poster() {
      if (!this.isVideo) {
        return null;
      }
      return this.media.getAttribute('poster') || this.media.getAttribute('data-poster');
    }

    /**
     * Get the current aspect ratio in use
     */
    get ratio() {
      if (!this.isVideo) {
        return null;
      }
      const ratio = reduceAspectRatio(getAspectRatio.call(this));
      return is.array(ratio) ? ratio.join(':') : ratio;
    }

    /**
     * Set video aspect ratio
     */
    set ratio(input) {
      if (!this.isVideo) {
        this.debug.warn('Aspect ratio can only be set for video');
        return;
      }
      if (!is.string(input) || !validateAspectRatio(input)) {
        this.debug.error(`Invalid aspect ratio specified (${input})`);
        return;
      }
      this.config.ratio = reduceAspectRatio(input);
      setAspectRatio.call(this);
    }

    /**
     * Set the autoplay state
     * @param {Boolean} input - Whether to autoplay or not
     */
    set autoplay(input) {
      this.config.autoplay = is.boolean(input) ? input : this.config.autoplay;
    }

    /**
     * Get the current autoplay state
     */
    get autoplay() {
      return Boolean(this.config.autoplay);
    }

    /**
     * Toggle captions
     * @param {Boolean} input - Whether to enable captions
     */
    toggleCaptions(input) {
      captions.toggle.call(this, input, false);
    }

    /**
     * Set the caption track by index
     * @param {Number} input - Caption index
     */
    set currentTrack(input) {
      captions.set.call(this, input, false);
      captions.setup.call(this);
    }

    /**
     * Get the current caption track index (-1 if disabled)
     */
    get currentTrack() {
      const {
        toggled,
        currentTrack
      } = this.captions;
      return toggled ? currentTrack : -1;
    }

    /**
     * Set the wanted language for captions
     * Since tracks can be added later it won't update the actual caption track until there is a matching track
     * @param {String} input - Two character ISO language code (e.g. EN, FR, PT, etc)
     */
    set language(input) {
      captions.setLanguage.call(this, input, false);
    }

    /**
     * Get the current track's language
     */
    get language() {
      return (captions.getCurrentTrack.call(this) || {}).language;
    }

    /**
     * Toggle picture-in-picture playback on WebKit/MacOS
     * TODO: update player with state, support, enabled
     * TODO: detect outside changes
     */
    set pip(input) {
      // Bail if no support
      if (!support.pip) {
        return;
      }

      // Toggle based on current state if not passed
      const toggle = is.boolean(input) ? input : !this.pip;

      // Toggle based on current state
      // Safari
      if (is.function(this.media.webkitSetPresentationMode)) {
        this.media.webkitSetPresentationMode(toggle ? pip.active : pip.inactive);
      }

      // Chrome
      if (is.function(this.media.requestPictureInPicture)) {
        if (!this.pip && toggle) {
          this.media.requestPictureInPicture();
        } else if (this.pip && !toggle) {
          document.exitPictureInPicture();
        }
      }
    }

    /**
     * Get the current picture-in-picture state
     */
    get pip() {
      if (!support.pip) {
        return null;
      }

      // Safari
      if (!is.empty(this.media.webkitPresentationMode)) {
        return this.media.webkitPresentationMode === pip.active;
      }

      // Chrome
      return this.media === document.pictureInPictureElement;
    }

    /**
     * Sets the preview thumbnails for the current source
     */
    setPreviewThumbnails(thumbnailSource) {
      if (this.previewThumbnails && this.previewThumbnails.loaded) {
        this.previewThumbnails.destroy();
        this.previewThumbnails = null;
      }
      Object.assign(this.config.previewThumbnails, thumbnailSource);

      // Create new instance if it is still enabled
      if (this.config.previewThumbnails.enabled) {
        this.previewThumbnails = new PreviewThumbnails(this);
      }
    }
    /**
     * Check for support
     * @param {String} type - Player type (audio/video)
     * @param {String} provider - Provider (html5/youtube/vimeo)
     */
    static supported(type, provider) {
      return support.check(type, provider);
    }

    /**
     * Load an SVG sprite into the page
     * @param {String} url - URL for the SVG sprite
     * @param {String} [id] - Unique ID
     */
    static loadSprite(url, id) {
      return loadSprite(url, id);
    }

    /**
     * Setup multiple instances
     * @param {*} selector
     * @param {Object} options
     */
    static setup(selector, options = {}) {
      let targets = null;
      if (is.string(selector)) {
        targets = Array.from(document.querySelectorAll(selector));
      } else if (is.nodeList(selector)) {
        targets = Array.from(selector);
      } else if (is.array(selector)) {
        targets = selector.filter(is.element);
      }
      if (is.empty(targets)) {
        return null;
      }
      return targets.map(t => new Plyr(t, options));
    }
  }
  Plyr.defaults = cloneDeep(defaults);

  return Plyr;

}));


(function(n){var g=function(b){return document.querySelectorAll(b)[0]},b=function(b,g){return b?b[g]||"":""},w=function(b,g){if(b)for(var d=b.length,h=0;h<d;h++)g(h,b[h])},z=function(b,g,d){g=[g.toLowerCase(),"webkit".concat(g),"MS".concat(g),"o".concat(g)];w(g,function(h,g){b[g]=d})},D=function(b,g,d){d=[d.toLowerCase(),"webkit".concat(d),"MS".concat(d),"o".concat(d)];w(d,function(d,l){b.addEventListener(l,g,!1)})},M=function(b,g){D(b,g,"AnimationEnd")},R=function(b,g){b.transitionEndEvent||(b.transitionEndEvent=
!0,D(b,g,"TransitionEnd"))},G=function(b,g){b.firstChild?b.insertBefore(g,b.firstChild):b.appendChild(g)},m=function(l,m){var d=this,h=function(a,e){var c=function(a){return"undefined"!==typeof a};return e?c(m[a])?c(m[a][e])?m[a][e]:F[a][e]:F[a][e]:c(m[a])?m[a]:F[a]},L=function(a,e){try{if(e){if(document.fullscreenElement||document.webkitFullscreenElement||document.mozFullScreenElement||document.msFullscreenElement)if(document.exitFullscreen)document.exitFullscreen()["catch"](function(){});else if(document.mozCancelFullScreen)document.mozCancelFullScreen()["catch"](function(){});
else if(document.mozCancelFullScreen)document.mozCancelFullScreen()["catch"](function(){})}else if(a.requestFullScreen)a.requestFullScreen();else if(a["ms".concat("RequestFullScreen")])a["ms".concat("RequestFullScreen")]();else if(a["moz".concat("RequestFullScreen")])a["moz".concat("RequestFullScreen")]();else if(a["webkit".concat("RequestFullScreen")])a["webkit".concat("RequestFullScreen")]()}catch(c){console.warn("[Zuck.js] Can't access fullscreen")}},y=function(a,e,c,d){var b=0<e?1:-1;b*=Math.abs(e)/
g("#zuck-modal").offsetWidth*90;if(h("cubeEffect")){var f=0===b?"scale(0.95)":"scale(0.930,0.930)";z(g("#zuck-modal-content").style,"Transform",f);if(-90>b||90<b)return!1}e=h("cubeEffect")?"rotateY(".concat(b,"deg)"):"translate3d(".concat(e,"px, 0, 0)");a&&(z(a.style,"TransitionTimingFunction",d),z(a.style,"TransitionDuration","".concat(c,"ms")),z(a.style,"Transform",e))},A=function(a,e,c,d){var b=0,f=0;if(a){if(a.offsetParent){do if(b+=a.offsetLeft,f+=a.offsetTop,a===d)break;while(a=a.offsetParent)
}e&&(f-=e);c&&(b-=c)}return[b,f]};"string"===typeof l&&(l=document.getElementById(l));l.id||l.setAttribute("id","stories-"+Math.random().toString(36).substr(2,9));var H=function(a){a=1E3*Number(a);a=new Date(a);var e=a.getTime();e=((new Date).getTime()-e)/1E3;var c=h("language","time");c=[[60," ".concat(c.seconds),1],[120,"1 ".concat(c.minute),""],[3600," ".concat(c.minutes),60],[7200,"1 ".concat(c.hour),""],[86400," ".concat(c.hours),3600],[172800," ".concat(c.yesterday),""],[604800," ".concat(c.days),
86400]];var d=1;0>e&&(e=Math.abs(e),d=2);for(var b=0,f;f=c[b++];)if(e<f[0])return"string"===typeof f[2]?f[d]:Math.floor(e/f[2])+f[1];e=a.getDate();c=a.getMonth();a=a.getFullYear();return"".concat(e,"/").concat(c+1,"/").concat(a)},k=l.id,F={skin:"snapgram",avatars:!0,stories:[],backButton:!0,backNative:!1,paginationArrows:!1,previousTap:!0,autoFullScreen:!1,openEffect:!0,cubeEffect:!1,list:!1,localStorage:!0,callbacks:{onOpen:function(a,d){d()},onView:function(a){},onEnd:function(a,d){d()},onClose:function(a,
d){d()},onNextItem:function(a,d,c){c()},onNavigateItem:function(a,d,c){c()}},template:{timelineItem:function(a){return'\n<div class="story '.concat(!0===b(a,"seen")?"seen":"",'">\n<a class="item-link" href="').concat(b(a,"link"),'">\n<span class="item-preview">\n<img lazy="eager" src="').concat(h("avatars")||!b(a,"currentPreview")?b(a,"photo"):b(a,"currentPreview"),'" />\n</span>\n<span class="info" itemProp="author" itemScope itemType="http://schema.org/Person">\n<strong class="name" itemProp="name">').concat(b(a,
"name"),'</strong>\n<span class="time">').concat(b(a,"lastUpdatedAgo"),'</span>\n</span>\n</a>\n\n<ul class="items"></ul>\n</div>')},timelineStoryItem:function(a){return'<a href="'.concat(b(a,"src"),'"\ndata-link="').concat(b(a,"link"),'"\ndata-linkText="').concat(b(a,"linkText"),'"\ndata-time="').concat(b(a,"time"),'"\ndata-type="').concat(b(a,
"type"),'"\ndata-length="').concat(b(a,"length"),'">\n<img loading="auto" src="').concat(b(a,"preview"),'" />\n</a>')},viewerItem:function(a,d){return'<div class="story-viewer">\n<div class="head">\n<div class="left">\n'.concat(h("backButton")?'<a class="back">&lsaquo;</a>':"",'\n\n<span class="item-preview">\n<img lazy="eager" class="profilePhoto" src="').concat(b(a,
"photo"),'" />\n</span>\n\n<div class="info">\n<strong class="name">').concat(b(a,"name"),'</strong>\n<span class="time">').concat(b(a,"timeAgo"),'</span>\n</div>\n</div>\n\n<div class="right">\n<span class="time">').concat(b(d,"timeAgo"),'</span>\n<span class="loading"></span>\n<a class="close" tabIndex="2">&times;</a>\n</div>\n</div>\n\n<div class="slides-pointers">\n<div class="wrap"></div>\n</div>\n\n').concat(h("paginationArrows")?
'<div class="slides-pagination">\n<span class="previous">&lsaquo;</span>\n<span class="next">&rsaquo;</span>\n</div>':"","\n</div>")},viewerItemPointer:function(a,d,c){return'<span \nclass="'.concat(d===a?"active":""," ").concat(!0===b(c,"seen")?"seen":"",'"\ndata-index="').concat(a,'" data-item-id="').concat(b(c,"id"),'">\n<b style="animation-duration:').concat(""===
b(c,"length")?"3":b(c,"length"),'s"></b>\n</span>')},viewerItemBody:function(a,d,c){return'<div \nclass="item '.concat(!0===b(c,"seen")?"seen":""," ").concat(d===a?"active":"",'"\ndata-time="').concat(b(c,"time"),'" data-type="').concat(b(c,"type"),'" data-index="').concat(a,'" data-item-id="').concat(b(c,"id"),'">\n').concat("video"===b(c,"type")?'<video class="media" muted webkit-playsinline playsinline preload="auto" src="'.concat(b(c,
"src"),'" ').concat(b(c,"type"),'></video>\n<b class="tip muted">').concat(h("language","unmute"),"</b>"):'<img loading="auto" class="media" src="'.concat(b(c,"src"),'" ').concat(b(c,"type")," />\n"),"\n\n").concat(b(c,"link")?'<a class="tip link" href="'.concat(b(c,"link"),'" rel="noopener" target="_blank">\n').concat(b(c,"linkText")&&""!==b(c,"linkText")?b(c,"linkText"):h("language","visitLink"),"\n</a>"):
"","\n</div>")}},language:{unmute:"Touch to unmute",keyboardTip:"Press space to see next",visitLink:"Visit link",time:{ago:"ago",hour:"hour ago",hours:"hours ago",minute:"minute ago",minutes:"minutes ago",fromnow:"from now",seconds:"seconds ago",yesterday:"yesterday",tomorrow:"tomorrow",days:"days ago"}}},B=function(){var a=g("#zuck-modal");a||d.hasModal||(d.hasModal=!0,a=document.createElement("div"),a.id="zuck-modal",h("cubeEffect")&&(a.className="with-cube"),a.innerHTML='<div id="zuck-modal-content"></div>',
a.style.display="none",a.setAttribute("tabIndex","1"),a.onkeyup=function(a){a=a.keyCode;27===a?B.close():(13===a||32===a)&&B.next()},h("openEffect")&&a.classList.add("with-effects"),R(a,function(){a.classList.contains("closed")&&(e.innerHTML="",a.style.display="none",a.classList.remove("closed"),a.classList.remove("animated"))}),document.body.appendChild(a));var e=g("#zuck-modal-content"),c=function(a){var c=g("#zuck-modal"),b="",e="",f=0,p=g("#zuck-modal-slider-".concat(k)),r={previous:g("#zuck-modal .story-viewer.previous"),
next:g("#zuck-modal .story-viewer.next"),viewing:g("#zuck-modal .story-viewer.viewing")};if(!r.previous&&!a||!r.next&&a)return!1;a?(b="next",e="previous"):(b="previous",e="next");h("cubeEffect")?"previous"===b?f=c.slideWidth:"next"===b&&(f=-1*c.slideWidth):f=-1*A(r[b])[0];y(p,f,600,null);setTimeout(function(){if(""!==b&&r[b]&&""!==e){var a=r[b].getAttribute("data-story-id");d.internalData.currentStory=a;var c=g("#zuck-modal .story-viewer.".concat(e));c&&c.parentNode.removeChild(c);r.viewing&&(r.viewing.classList.add("stopped"),
r.viewing.classList.add(e),r.viewing.classList.remove("viewing"));r[b]&&(r[b].classList.remove("stopped"),r[b].classList.remove(b),r[b].classList.add("viewing"));(c=I(b))&&q(c,b);var f=d.internalData.currentStory;if(c=g('#zuck-modal [data-story-id="'.concat(f,'"]'))){c=c.querySelectorAll("[data-index].active");var v=c[0].firstElementChild;d.data[f].currentItem=parseInt(c[0].getAttribute("data-index"),10);c[0].innerHTML='<b style="'.concat(v.style.cssText,'"></b>');M(c[0].firstElementChild,function(){d.nextItem(!1)})}y(p,
"0",0,null);c&&(a=g('#zuck-modal .story-viewer[data-story-id="'.concat(a,'"]')),E(a,[c[0],c[1]],!0));h("callbacks","onView")(d.internalData.currentStory)}},650)},q=function(a,c,e){var f=g("#zuck-modal-slider-".concat(k)),q=b(a,"items");a.timeAgo=q&&q[0]?H(b(q[0],"time")):"";var v="",p="",l=b(a,"id"),m=document.createElement("div"),x=b(a,"currentItem")||0;if(g('#zuck-modal .story-viewer[data-story-id="'.concat(l,'"]')))return!1;m.className="slides";w(q,function(c,d){d.timeAgo=H(b(d,"time"));x>c&&(a.items[c].timeAgo=
d.timeAgo,a.items[c].seen=!0,d.seen=!0);p+=h("template","viewerItemPointer")(c,x,d);v+=h("template","viewerItemBody")(c,x,d)});m.innerHTML=v;var t=m.querySelector("video"),n=function(a){a.muted?u.classList.add("muted"):u.classList.remove("muted")};t&&(t.onwaiting=function(a){t.paused&&(u.classList.add("paused"),u.classList.add("loading"))},t.onplay=function(){n(t);u.classList.remove("stopped");u.classList.remove("paused");u.classList.remove("loading")},t.onload=t.onplaying=t.oncanplay=function(){n(t);
u.classList.remove("loading")},t.onvolumechange=function(){n(t)});q=document.createElement("div");q.innerHTML=h("template","viewerItem")(a,x);var u=q.firstElementChild;u.className="story-viewer muted ".concat(c," ").concat(e?"":"stopped"," ").concat(h("backButton")?"with-back-button":"");u.setAttribute("data-story-id",l);u.querySelector(".slides-pointers .wrap").innerHTML=p;w(u.querySelectorAll(".close, .back"),function(a,c){c.onclick=function(a){a.preventDefault();B.close()}});u.appendChild(m);"viewing"===
c&&E(u,u.querySelectorAll('[data-index="'.concat(x,'"].active')),!1);w(u.querySelectorAll(".slides-pointers [data-index] > b"),function(a,c){M(c,function(){d.nextItem(!1)})});"previous"===c?G(f,u):f.appendChild(u)},p=function(a){var b=g("#zuck-modal"),e,f=void 0,q=void 0,p=void 0,r=void 0,l=void 0,k=function(c){var d=g("#zuck-modal .viewing");if("A"!==c.target.nodeName){var h=c.touches?c.touches[0]:c,v=A(g("#zuck-modal .story-viewer.viewing"));b.slideWidth=g("#zuck-modal .story-viewer").offsetWidth;
b.slideHeight=g("#zuck-modal .story-viewer").offsetHeight;e=v[0];v=h.clientY;f={x:h.clientX,y:v,time:Date.now(),valid:!0};80>v||v>b.slideHeight-80?f.valid=!1:(c.preventDefault(),q=void 0,p={},a.addEventListener("mousemove",m),a.addEventListener("mouseup",t),a.addEventListener("mouseleave",t),a.addEventListener("touchmove",m),a.addEventListener("touchend",t),d&&d.classList.add("paused"),S(),r=setTimeout(function(){d.classList.add("longPress")},600),l=setTimeout(function(){clearInterval(l);l=!1},250))}},
m=function(c){var d=c.touches?c.touches[0]:c,b=d.clientX;d=d.clientY;f&&f.valid&&(p={x:b-f.x,y:d-f.y},"undefined"===typeof q&&(q=!!(q||Math.abs(p.x)<Math.abs(p.y))),!q&&f&&(c.preventDefault(),y(a,e+p.x,0,null)))},t=function J(v){var k=g("#zuck-modal .viewing"),u=f,x=f?Date.now()-f.time:void 0;x=300>Number(x)&&25<Math.abs(p.x)||Math.abs(p.x)>b.slideWidth/3;var C=0>p.x,t=C?g("#zuck-modal .story-viewer.next"):g("#zuck-modal .story-viewer.previous");t=C&&!t||!C&&!t;if(!f||f.valid)if(p&&(q||(x&&!t?c(C):
y(a,e,300)),f=void 0,a.removeEventListener("mousemove",m),a.removeEventListener("mouseup",J),a.removeEventListener("mouseleave",J),a.removeEventListener("touchmove",m),a.removeEventListener("touchend",J)),x=d.internalData.currentVideoElement,r&&clearInterval(r),k&&(E(k,k.querySelectorAll(".active"),!1),k.classList.remove("longPress"),k.classList.remove("paused")),l)if(clearInterval(l),l=!1,k=function(){C||(u.x>n.screen.width/3||!h("previousTap")?d.navigateItem("next",v):d.navigateItem("previous",
v))},(t=g("#zuck-modal .viewing"))&&x)t.classList.contains("muted")?N(x,t):k();else return k(),!1};a.addEventListener("touchstart",k);a.addEventListener("mousedown",k)};return{show:function(a,c){var b=g("#zuck-modal");h("callbacks","onOpen")(a,function(){e.innerHTML='<div id="zuck-modal-slider-'.concat(k,'" class="slider"></div>');var c=d.data[a],f=c.currentItem||0,v=g("#zuck-modal-slider-".concat(k));p(v);d.internalData.currentStory=a;c.currentItem=f;h("backNative")&&(n.location.hash="#!".concat(k));
(f=I("previous"))&&q(f,"previous");q(c,"viewing",!0);(c=I("next"))&&q(c,"next");h("autoFullScreen")&&b.classList.add("fullscreen");var l=function(){b.classList.contains("fullscreen")&&h("autoFullScreen")&&1024>=n.screen.width&&L(b);b.focus()};h("openEffect")?(c=g("#".concat(k,' [data-id="').concat(a,'"] .item-preview')),f=A(c),b.style.marginLeft="".concat(f[0]+c.offsetWidth/2,"px"),b.style.marginTop="".concat(f[1]+c.offsetHeight/2,"px"),b.style.display="block",b.slideWidth=g("#zuck-modal .story-viewer").offsetWidth,
setTimeout(function(){b.classList.add("animated")},10),setTimeout(function(){l()},300)):(b.style.display="block",b.slideWidth=g("#zuck-modal .story-viewer").offsetWidth,l());h("callbacks","onView")(a)})},next:function(a){h("callbacks","onEnd")(d.internalData.currentStory,function(){var a=d.internalData.currentStory,b=g("#".concat(k,' [data-id="').concat(a,'"]'));b&&(b.classList.add("seen"),d.data[a].seen=!0,d.internalData.seenItems[a]=!0,O("seenItems",d.internalData.seenItems),K());g("#zuck-modal .story-viewer.next")?
c(!0):B.close()})},close:function(){var a=g("#zuck-modal");h("callbacks","onClose")(d.internalData.currentStory,function(){h("backNative")&&(n.location.hash="");L(a,!0);h("openEffect")?a.classList.add("closed"):(e.innerHTML="",a.style.display="none")})}}}(),D=function(a,b){var c=a.getAttribute("data-id"),e=document.querySelectorAll("#".concat(k,' [data-id="').concat(c,'"] .items > li')),g=[];if(!h("reactive")||b)w(e,function(a,c){var b=c.firstElementChild,d=b.firstElementChild;g.push({id:b.getAttribute("data-id"),
src:b.getAttribute("href"),length:b.getAttribute("data-length"),type:b.getAttribute("data-type"),time:b.getAttribute("data-time"),link:b.getAttribute("data-link"),linkText:b.getAttribute("data-linkText"),preview:d.getAttribute("src")})}),d.data[c].items=g,(c=h("callbacks","onDataUpdate"))&&c(d.data,function(){})},P=function(a,b){var c=a.getAttribute("data-id"),e=!1;d.internalData.seenItems[c]&&(e=!0);try{d.data[c]||(d.data[c]={}),d.data[c].id=c,d.data[c].photo=a.getAttribute("data-photo"),d.data[c].name=
a.querySelector(".name").innerText,d.data[c].link=a.querySelector(".item-link").getAttribute("href"),d.data[c].lastUpdated=a.getAttribute("data-last-updated"),d.data[c].seen=e,d.data[c].items||(d.data[c].items=[],d.data[c].noItems=!0)}catch(p){d.data[c]={items:[]}}a.onclick=function(a){a.preventDefault();B.show(c)};(e=h("callbacks","onDataUpdate"))&&e(d.data,function(){})},I=function(a){var b=d.internalData.currentStory;a="".concat(a,"ElementSibling");return b&&(b=g("#".concat(k,' [data-id="').concat(b,
'"]'))[a])?(b=b.getAttribute("data-id"),d.data[b]||!1):!1},K=function(){w(document.querySelectorAll("#".concat(k," .story.seen")),function(a,b){var c=d.data[b.getAttribute("data-id")],e=b.parentNode;h("reactive")||e.removeChild(b);d.update(c,!0)})},E=function(a,b,c){var e=b[1],g=b[0];if(!e||!g)return!1;(b=d.internalData.currentVideoElement)&&b.pause();if("video"===e.getAttribute("data-type")){var f=e.getElementsByTagName("video")[0];if(!f)return d.internalData.currentVideoElement=!1;e=function(){f.duration&&
z(g.getElementsByTagName("b")[0].style,"AnimationDuration","".concat(f.duration,"s"))};e();f.addEventListener("loadedmetadata",e);d.internalData.currentVideoElement=f;f.play();c&&c.target&&N(f,a)}else d.internalData.currentVideoElement=!1},S=function(){var a=d.internalData.currentVideoElement;if(a)try{a.pause()}catch(e){}},N=function(a,b){a.muted=!1;a.volume=1;a.removeAttribute("muted");a.play();a.paused&&(a.muted=!0,a.play());b&&b.classList.remove("paused")},O=function(a,b){try{if(h("localStorage")){var c=
"zuck-".concat(k,"-").concat(a);n.localStorage[c]=JSON.stringify(b)}}catch(q){}},Q=function(a){return h("localStorage")?(a="zuck-".concat(k,"-").concat(a),n.localStorage[a]?JSON.parse(n.localStorage[a]):!1):!1};d.data=h("stories")||{};d.internalData={};d.internalData.seenItems=Q("seenItems")||{};d.add=d.update=function(a,e){var c=b(a,"id"),q=g("#".concat(k,' [data-id="').concat(c,'"]')),p=b(a,"items"),f=void 0;f=!1;p[0]&&(f=p[0].preview||"");!0===d.internalData.seenItems[c]&&(a.seen=!0);a.currentPreview=
f;q?f=q:(f=document.createElement("div"),f.innerHTML=h("template","timelineItem")(a),f=f.firstElementChild);!1===a.seen&&(d.internalData.seenItems[c]=!1,O("seenItems",d.internalData.seenItems));f.setAttribute("data-id",c);f.setAttribute("data-photo",b(a,"photo"));f.setAttribute("data-last-updated",b(a,"lastUpdated"));P(f);q||h("reactive")||(e?l.appendChild(f):G(l,f));w(p,function(a,b){d.addItem(c,b,e)});e||K()};d.next=function(){B.next()};d.remove=function(a){a=g("#".concat(k,' > [data-id="').concat(a,
'"]'));a.parentNode.removeChild(a)};d.addItem=function(a,d,c){a=g("#".concat(k,' > [data-id="').concat(a,'"]'));if(!h("reactive")){var e=document.createElement("li"),p=a.querySelectorAll(".items")[0];e.className=b(d,"seen")?"seen":"";e.setAttribute("data-id",b(d,"id"));e.innerHTML=h("template","timelineStoryItem")(d);c?p.appendChild(e):G(p,e)}D(a)};d.removeItem=function(a,b){var c=g("#".concat(k,' > [data-id="').concat(a,'"] [data-id="').concat(b,'"]'));h("reactive")||l.parentNode.removeChild(c)};
d.navigateItem=d.nextItem=function(a,b){var c=d.internalData.currentStory,e=d.data[c].currentItem,k=g('#zuck-modal .story-viewer[data-story-id="'.concat(c,'"]')),f="previous"===a?-1:1;if(!k||1===k.touchMove)return!1;var l=k.querySelectorAll('[data-index="'.concat(e,'"]')),m=l[0],n=l[1],y=k.querySelectorAll('[data-index="'.concat(e+f,'"]')),A=y[0],r=y[1];k&&A&&r?(e=(e=h("callbacks","onNavigateItem"))?h("callbacks","onNavigateItem"):h("callbacks","onNextItem"),e(c,r.getAttribute("data-story-id"),function(){"previous"===
a?(m.classList.remove("seen"),n.classList.remove("seen")):(m.classList.add("seen"),n.classList.add("seen"));m.classList.remove("active");n.classList.remove("active");A.classList.remove("seen");A.classList.add("active");r.classList.remove("seen");r.classList.add("active");w(k.querySelectorAll(".time"),function(a,b){b.innerText=H(r.getAttribute("data-time"))});d.data[c].currentItem+=f;E(k,y,b)})):k&&"previous"!==a&&B.next(b)};return function(){l&&l.querySelector(".story")&&w(l.querySelectorAll(".story"),
function(a,b){P(b)});h("backNative")&&(n.location.hash==="#!".concat(k)&&(n.location.hash=""),n.addEventListener("popstate",function(a){n.location.hash!=="#!".concat(k)&&(n.location.hash="")},!1));if(!h("reactive")){var a=Q("seenItems");for(b in a)a.hasOwnProperty(b)&&d.data[b]&&(d.data[b].seen=a[b])}w(h("stories"),function(a,b){d.add(b,!0)});K();a=h("avatars")?"user-icon":"story-preview";var b=h("list")?"list":"carousel";l.className+=" stories ".concat(a," ").concat(b," ").concat("".concat(h("skin")).toLowerCase());
return d}()};m.buildTimelineItem=function(b,g,d,h,n,y){var l={id:b,photo:g,name:d,link:h,lastUpdated:n,items:[]};w(y,function(b,d){l.items.push(m.buildStoryItem.apply(m,d))});return l};m.buildStoryItem=function(b,g,d,h,m,n,w,z,k){return{id:b,type:g,length:d,src:h,preview:m,link:n,linkText:w,seen:z,time:k}};m.buildItem=m.buildStoryItem;"undefined"!==typeof exports?("undefined"!==typeof module&&module.exports&&(exports=module.exports=m),exports.ZuckJS=m):n.ZuckitaDaGalera=n.Zuck=m;return m})(window||{});
/*!
 * OverlayScrollbars
 * https://github.com/KingSora/OverlayScrollbars
 *
 * Version: 1.13.3
 *
 * Copyright KingSora | Rene Haas.
 * https://github.com/KingSora
 *
 * Released under the MIT license.
 * Date: 20.07.2022
 */
!function(n,t){"function"==typeof define&&define.amd?define(function(){return t(n,n.document,undefined)}):"object"==typeof module&&"object"==typeof module.exports?module.exports=t(n,n.document,undefined):t(n,n.document,undefined)}("undefined"!=typeof window?window:this,function(vi,hi,di){"use strict";var o,l,a,u,pi="object",bi="function",mi="array",gi="string",wi="boolean",yi="number",f="undefined",n="null",xi={c:"class",s:"style",i:"id",l:"length",p:"prototype",ti:"tabindex",oH:"offsetHeight",cH:"clientHeight",sH:"scrollHeight",oW:"offsetWidth",cW:"clientWidth",sW:"scrollWidth",hOP:"hasOwnProperty",bCR:"getBoundingClientRect"},_i=(o={},l={},{e:a=["-webkit-","-moz-","-o-","-ms-"],u:u=["WebKit","Moz","O","MS"],v:function(n){var t=l[n];if(l[xi.hOP](n))return t;for(var r,e,i,o=c(n),u=hi.createElement("div")[xi.s],f=0;f<a.length;f++)for(i=a[f].replace(/-/g,""),r=[n,a[f]+n,i+o,c(i)+o],e=0;e<r[xi.l];e++)if(u[r[e]]!==di){t=r[e];break}return l[n]=t},d:function(n,t,r){var e=n+" "+t,i=l[e];if(l[xi.hOP](e))return i;for(var o,u=hi.createElement("div")[xi.s],f=t.split(" "),a=r||"",c=0,s=-1;c<f[xi.l];c++)for(;s<_i.e[xi.l];s++)if(o=s<0?f[c]:_i.e[s]+f[c],u.cssText=n+":"+o+a,u[xi.l]){i=o;break}return l[e]=i},m:function(n,t,r){var e=0,i=o[n];if(!o[xi.hOP](n)){for(i=vi[n];e<u[xi.l];e++)i=i||vi[(t?u[e]:u[e].toLowerCase())+c(n)];o[n]=i}return i||r}});function c(n){return n.charAt(0).toUpperCase()+n.slice(1)}var Oi={wW:r(t,0,!0),wH:r(t,0),mO:r(_i.m,0,"MutationObserver",!0),rO:r(_i.m,0,"ResizeObserver",!0),rAF:r(_i.m,0,"requestAnimationFrame",!1,function(n){return vi.setTimeout(n,1e3/60)}),cAF:r(_i.m,0,"cancelAnimationFrame",!1,function(n){return vi.clearTimeout(n)}),now:function(){return Date.now&&Date.now()||(new Date).getTime()},stpP:function(n){n.stopPropagation?n.stopPropagation():n.cancelBubble=!0},prvD:function(n){n.preventDefault&&n.cancelable?n.preventDefault():n.returnValue=!1},page:function(n){var t=((n=n.originalEvent||n).target||n.srcElement||hi).ownerDocument||hi,r=t.documentElement,e=t.body;if(n.touches===di)return!n.pageX&&n.clientX&&null!=n.clientX?{x:n.clientX+(r&&r.scrollLeft||e&&e.scrollLeft||0)-(r&&r.clientLeft||e&&e.clientLeft||0),y:n.clientY+(r&&r.scrollTop||e&&e.scrollTop||0)-(r&&r.clientTop||e&&e.clientTop||0)}:{x:n.pageX,y:n.pageY};var i=n.touches[0];return{x:i.pageX,y:i.pageY}},mBtn:function(n){var t=n.button;return n.which||t===di?n.which:1&t?1:2&t?3:4&t?2:0},inA:function(n,t){for(var r=0;r<t[xi.l];r++)try{if(t[r]===n)return r}catch(e){}return-1},isA:function(n){var t=Array.isArray;return t?t(n):this.type(n)==mi},type:function(n){return n===di||null===n?n+"":Object[xi.p].toString.call(n).replace(/^\[object (.+)\]$/,"$1").toLowerCase()},bind:r};function t(n){return n?vi.innerWidth||hi.documentElement[xi.cW]||hi.body[xi.cW]:vi.innerHeight||hi.documentElement[xi.cH]||hi.body[xi.cH]}function r(n,t){if(typeof n!=bi)throw"Can't bind function!";var r=xi.p,e=Array[r].slice.call(arguments,2),i=function(){},o=function(){return n.apply(this instanceof i?this:t,e.concat(Array[r].slice.call(arguments)))};return n[r]&&(i[r]=n[r]),o[r]=new i,o}var s,v,h,k,I,T,d,p,Si=Math,zi=vi.jQuery,A=(s={p:Si.PI,c:Si.cos,s:Si.sin,w:Si.pow,t:Si.sqrt,n:Si.asin,a:Si.abs,o:1.70158},{swing:function(n,t,r,e,i){return.5-s.c(n*s.p)/2},linear:function(n,t,r,e,i){return n},easeInQuad:function(n,t,r,e,i){return e*(t/=i)*t+r},easeOutQuad:function(n,t,r,e,i){return-e*(t/=i)*(t-2)+r},easeInOutQuad:function(n,t,r,e,i){return(t/=i/2)<1?e/2*t*t+r:-e/2*(--t*(t-2)-1)+r},easeInCubic:function(n,t,r,e,i){return e*(t/=i)*t*t+r},easeOutCubic:function(n,t,r,e,i){return e*((t=t/i-1)*t*t+1)+r},easeInOutCubic:function(n,t,r,e,i){return(t/=i/2)<1?e/2*t*t*t+r:e/2*((t-=2)*t*t+2)+r},easeInQuart:function(n,t,r,e,i){return e*(t/=i)*t*t*t+r},easeOutQuart:function(n,t,r,e,i){return-e*((t=t/i-1)*t*t*t-1)+r},easeInOutQuart:function(n,t,r,e,i){return(t/=i/2)<1?e/2*t*t*t*t+r:-e/2*((t-=2)*t*t*t-2)+r},easeInQuint:function(n,t,r,e,i){return e*(t/=i)*t*t*t*t+r},easeOutQuint:function(n,t,r,e,i){return e*((t=t/i-1)*t*t*t*t+1)+r},easeInOutQuint:function(n,t,r,e,i){return(t/=i/2)<1?e/2*t*t*t*t*t+r:e/2*((t-=2)*t*t*t*t+2)+r},easeInSine:function(n,t,r,e,i){return-e*s.c(t/i*(s.p/2))+e+r},easeOutSine:function(n,t,r,e,i){return e*s.s(t/i*(s.p/2))+r},easeInOutSine:function(n,t,r,e,i){return-e/2*(s.c(s.p*t/i)-1)+r},easeInExpo:function(n,t,r,e,i){return 0==t?r:e*s.w(2,10*(t/i-1))+r},easeOutExpo:function(n,t,r,e,i){return t==i?r+e:e*(1-s.w(2,-10*t/i))+r},easeInOutExpo:function(n,t,r,e,i){return 0==t?r:t==i?r+e:(t/=i/2)<1?e/2*s.w(2,10*(t-1))+r:e/2*(2-s.w(2,-10*--t))+r},easeInCirc:function(n,t,r,e,i){return-e*(s.t(1-(t/=i)*t)-1)+r},easeOutCirc:function(n,t,r,e,i){return e*s.t(1-(t=t/i-1)*t)+r},easeInOutCirc:function(n,t,r,e,i){return(t/=i/2)<1?-e/2*(s.t(1-t*t)-1)+r:e/2*(s.t(1-(t-=2)*t)+1)+r},easeInElastic:function(n,t,r,e,i){var o=s.o,u=0,f=e;return 0==t?r:1==(t/=i)?r+e:(u=u||.3*i,o=f<s.a(e)?(f=e,u/4):u/(2*s.p)*s.n(e/f),-(f*s.w(2,10*--t)*s.s((t*i-o)*(2*s.p)/u))+r)},easeOutElastic:function(n,t,r,e,i){var o=s.o,u=0,f=e;return 0==t?r:1==(t/=i)?r+e:(u=u||.3*i,o=f<s.a(e)?(f=e,u/4):u/(2*s.p)*s.n(e/f),f*s.w(2,-10*t)*s.s((t*i-o)*(2*s.p)/u)+e+r)},easeInOutElastic:function(n,t,r,e,i){var o=s.o,u=0,f=e;return 0==t?r:2==(t/=i/2)?r+e:(u=u||i*(.3*1.5),o=f<s.a(e)?(f=e,u/4):u/(2*s.p)*s.n(e/f),t<1?f*s.w(2,10*--t)*s.s((t*i-o)*(2*s.p)/u)*-.5+r:f*s.w(2,-10*--t)*s.s((t*i-o)*(2*s.p)/u)*.5+e+r)},easeInBack:function(n,t,r,e,i,o){return e*(t/=i)*t*(((o=o||s.o)+1)*t-o)+r},easeOutBack:function(n,t,r,e,i,o){return e*((t=t/i-1)*t*(((o=o||s.o)+1)*t+o)+1)+r},easeInOutBack:function(n,t,r,e,i,o){return o=o||s.o,(t/=i/2)<1?e/2*(t*t*((1+(o*=1.525))*t-o))+r:e/2*((t-=2)*t*((1+(o*=1.525))*t+o)+2)+r},easeInBounce:function(n,t,r,e,i){return e-this.easeOutBounce(n,i-t,0,e,i)+r},easeOutBounce:function(n,t,r,e,i){var o=7.5625;return(t/=i)<1/2.75?e*(o*t*t)+r:t<2/2.75?e*(o*(t-=1.5/2.75)*t+.75)+r:t<2.5/2.75?e*(o*(t-=2.25/2.75)*t+.9375)+r:e*(o*(t-=2.625/2.75)*t+.984375)+r},easeInOutBounce:function(n,t,r,e,i){return t<i/2?.5*this.easeInBounce(n,2*t,0,e,i)+r:.5*this.easeOutBounce(n,2*t-i,0,e,i)+.5*e+r}}),Ci=(v=/[^\x20\t\r\n\f]+/g,h=" ",k="scrollLeft",I="scrollTop",T=[],d=Oi.type,p={animationIterationCount:!0,columnCount:!0,fillOpacity:!0,flexGrow:!0,flexShrink:!0,fontWeight:!0,lineHeight:!0,opacity:!0,order:!0,orphans:!0,widows:!0,zIndex:!0,zoom:!0},M[xi.p]={on:function(t,r){var e,i=(t=(t||"").match(v)||[""])[xi.l],o=0;return this.each(function(){e=this;try{if(e.addEventListener)for(;o<i;o++)e.addEventListener(t[o],r);else if(e.detachEvent)for(;o<i;o++)e.attachEvent("on"+t[o],r)}catch(n){}})},off:function(t,r){var e,i=(t=(t||"").match(v)||[""])[xi.l],o=0;return this.each(function(){e=this;try{if(e.removeEventListener)for(;o<i;o++)e.removeEventListener(t[o],r);else if(e.detachEvent)for(;o<i;o++)e.detachEvent("on"+t[o],r)}catch(n){}})},one:function(n,i){return n=(n||"").match(v)||[""],this.each(function(){var e=M(this);M.each(n,function(n,t){var r=function(n){i.call(this,n),e.off(t,r)};e.on(t,r)})})},trigger:function(n){var t,r;return this.each(function(){t=this,hi.createEvent?((r=hi.createEvent("HTMLEvents")).initEvent(n,!0,!1),t.dispatchEvent(r)):t.fireEvent("on"+n)})},append:function(n){return this.each(function(){i(this,"beforeend",n)})},prepend:function(n){return this.each(function(){i(this,"afterbegin",n)})},before:function(n){return this.each(function(){i(this,"beforebegin",n)})},after:function(n){return this.each(function(){i(this,"afterend",n)})},remove:function(){return this.each(function(){var n=this.parentNode;null!=n&&n.removeChild(this)})},unwrap:function(){var n,t,r,e=[];for(this.each(function(){-1===H(r=this.parentNode,e)&&e.push(r)}),n=0;n<e[xi.l];n++){for(t=e[n],r=t.parentNode;t.firstChild;)r.insertBefore(t.firstChild,t);r.removeChild(t)}return this},wrapAll:function(n){for(var t,r=this,e=M(n)[0],i=e,o=r[0].parentNode,u=r[0].previousSibling;0<i.childNodes[xi.l];)i=i.childNodes[0];for(t=0;r[xi.l]-t;i.firstChild===r[0]&&t++)i.appendChild(r[t]);var f=u?u.nextSibling:o.firstChild;return o.insertBefore(e,f),this},wrapInner:function(r){return this.each(function(){var n=M(this),t=n.contents();t[xi.l]?t.wrapAll(r):n.append(r)})},wrap:function(n){return this.each(function(){M(this).wrapAll(n)})},css:function(n,t){var r,e,i,o=vi.getComputedStyle;return d(n)==gi?t===di?(r=this[0],i=o?o(r,null):r.currentStyle[n],o?null!=i?i.getPropertyValue(n):r[xi.s][n]:i):this.each(function(){y(this,n,t)}):this.each(function(){for(e in n)y(this,e,n[e])})},hasClass:function(n){for(var t,r,e=0,i=h+n+h;t=this[e++];){if((r=t.classList)&&r.contains(n))return!0;if(1===t.nodeType&&-1<(h+g(t.className+"")+h).indexOf(i))return!0}return!1},addClass:function(n){var t,r,e,i,o,u,f,a,c=0,s=0;if(n)for(t=n.match(v)||[];r=this[c++];)if(a=r.classList,f===di&&(f=a!==di),f)for(;o=t[s++];)a.add(o);else if(i=r.className+"",e=1===r.nodeType&&h+g(i)+h){for(;o=t[s++];)e.indexOf(h+o+h)<0&&(e+=o+h);i!==(u=g(e))&&(r.className=u)}return this},removeClass:function(n){var t,r,e,i,o,u,f,a,c=0,s=0;if(n)for(t=n.match(v)||[];r=this[c++];)if(a=r.classList,f===di&&(f=a!==di),f)for(;o=t[s++];)a.remove(o);else if(i=r.className+"",e=1===r.nodeType&&h+g(i)+h){for(;o=t[s++];)for(;-1<e.indexOf(h+o+h);)e=e.replace(h+o+h,h);i!==(u=g(e))&&(r.className=u)}return this},hide:function(){return this.each(function(){this[xi.s].display="none"})},show:function(){return this.each(function(){this[xi.s].display="block"})},attr:function(n,t){for(var r,e=0;r=this[e++];){if(t===di)return r.getAttribute(n);r.setAttribute(n,t)}return this},removeAttr:function(n){return this.each(function(){this.removeAttribute(n)})},offset:function(){var n=this[0][xi.bCR](),t=vi.pageXOffset||hi.documentElement[k],r=vi.pageYOffset||hi.documentElement[I];return{top:n.top+r,left:n.left+t}},position:function(){var n=this[0];return{top:n.offsetTop,left:n.offsetLeft}},scrollLeft:function(n){for(var t,r=0;t=this[r++];){if(n===di)return t[k];t[k]=n}return this},scrollTop:function(n){for(var t,r=0;t=this[r++];){if(n===di)return t[I];t[I]=n}return this},val:function(n){var t=this[0];return n?(t.value=n,this):t.value},first:function(){return this.eq(0)},last:function(){return this.eq(-1)},eq:function(n){return M(this[0<=n?n:this[xi.l]+n])},find:function(t){var r,e=[];return this.each(function(){var n=this.querySelectorAll(t);for(r=0;r<n[xi.l];r++)e.push(n[r])}),M(e)},children:function(n){var t,r,e,i=[];return this.each(function(){for(r=this.children,e=0;e<r[xi.l];e++)t=r[e],(!n||t.matches&&t.matches(n)||w(t,n))&&i.push(t)}),M(i)},parent:function(n){var t,r=[];return this.each(function(){t=this.parentNode,n&&!M(t).is(n)||r.push(t)}),M(r)},is:function(n){var t,r;for(r=0;r<this[xi.l];r++){if(t=this[r],":visible"===n)return _(t);if(":hidden"===n)return!_(t);if(t.matches&&t.matches(n)||w(t,n))return!0}return!1},contents:function(){var n,t,r=[];return this.each(function(){for(n=this.childNodes,t=0;t<n[xi.l];t++)r.push(n[t])}),M(r)},each:function(n){return e(this,n)},animate:function(n,t,r,e){return this.each(function(){x(this,n,t,r,e)})},stop:function(n,t){return this.each(function(){!function f(n,t,r){for(var e,i,o,u=0;u<T[xi.l];u++)if((e=T[u]).el===n){if(0<e.q[xi.l]){if((i=e.q[0]).stop=!0,Oi.cAF()(i.frame),e.q.splice(0,1),r)for(o in i.props)W(n,o,i.props[o]);t?e.q=[]:N(e,!1)}break}}(this,n,t)})}},b(M,{extend:b,inArray:H,isEmptyObject:L,isPlainObject:R,each:e}),M);function b(){var n,t,r,e,i,o,u=arguments[0]||{},f=1,a=arguments[xi.l],c=!1;for(d(u)==wi&&(c=u,u=arguments[1]||{},f=2),d(u)!=pi&&!d(u)==bi&&(u={}),a===f&&(u=M,--f);f<a;f++)if(null!=(i=arguments[f]))for(e in i)n=u[e],u!==(r=i[e])&&(c&&r&&(R(r)||(t=Oi.isA(r)))?(o=t?(t=!1,n&&Oi.isA(n)?n:[]):n&&R(n)?n:{},u[e]=b(c,o,r)):r!==di&&(u[e]=r));return u}function H(n,t,r){for(var e=r||0;e<t[xi.l];e++)if(t[e]===n)return e;return-1}function E(n){return d(n)==bi}function L(n){for(var t in n)return!1;return!0}function R(n){if(!n||d(n)!=pi)return!1;var t,r=xi.p,e=Object[r].hasOwnProperty,i=e.call(n,"constructor"),o=n.constructor&&n.constructor[r]&&e.call(n.constructor[r],"isPrototypeOf");if(n.constructor&&!i&&!o)return!1;for(t in n);return d(t)==f||e.call(n,t)}function e(n,t){var r=0;if(m(n))for(;r<n[xi.l]&&!1!==t.call(n[r],r,n[r]);r++);else for(r in n)if(!1===t.call(n[r],r,n[r]))break;return n}function m(n){var t=!!n&&[xi.l]in n&&n[xi.l],r=d(n);return!E(r)&&(r==mi||0===t||d(t)==yi&&0<t&&t-1 in n)}function g(n){return(n.match(v)||[]).join(h)}function w(n,t){for(var r=(n.parentNode||hi).querySelectorAll(t)||[],e=r[xi.l];e--;)if(r[e]==n)return 1}function i(n,t,r){if(Oi.isA(r))for(var e=0;e<r[xi.l];e++)i(n,t,r[e]);else d(r)==gi?n.insertAdjacentHTML(t,r):n.insertAdjacentElement(t,r.nodeType?r:r[0])}function y(n,t,r){try{n[xi.s][t]!==di&&(n[xi.s][t]=function e(n,t){p[n.toLowerCase()]||d(t)!=yi||(t+="px");return t}(t,r))}catch(i){}}function N(n,t){var r,e;!1!==t&&n.q.splice(0,1),0<n.q[xi.l]?(e=n.q[0],x(n.el,e.props,e.duration,e.easing,e.complete,!0)):-1<(r=H(n,T))&&T.splice(r,1)}function W(n,t,r){t===k||t===I?n[t]=r:y(n,t,r)}function x(n,t,r,e,i,o){var u,f,a,c,s,l,v=R(r),h={},d={},p=0;for(l=v?(e=r.easing,r.start,a=r.progress,c=r.step,s=r.specialEasing,i=r.complete,r.duration):r,s=s||{},l=l||400,e=e||"swing",o=o||!1;p<T[xi.l];p++)if(T[p].el===n){f=T[p];break}for(u in f||(f={el:n,q:[]},T.push(f)),t)h[u]=u===k||u===I?n[u]:M(n).css(u);for(u in h)h[u]!==t[u]&&t[u]!==di&&(d[u]=t[u]);if(L(d))o&&N(f);else{var b,m,g,w,y,x,_,O,S,z=o?0:H(C,f.q),C={props:d,duration:v?r:l,easing:e,complete:i};if(-1===z&&(z=f.q[xi.l],f.q.push(C)),0===z)if(0<l)_=Oi.now(),O=function(){for(u in b=Oi.now(),S=b-_,m=C.stop||l<=S,g=1-(Si.max(0,_+l-b)/l||0),d)w=parseFloat(h[u]),y=parseFloat(d[u]),x=(y-w)*A[s[u]||e](g,g*l,0,1,l)+w,W(n,u,x),E(c)&&c(x,{elem:n,prop:u,start:w,now:x,end:y,pos:g,options:{easing:e,speacialEasing:s,duration:l,complete:i,step:c},startTime:_});E(a)&&a({},g,Si.max(0,l-S)),m?(N(f),E(i)&&i()):C.frame=Oi.rAF()(O)},C.frame=Oi.rAF()(O);else{for(u in d)W(n,u,d[u]);N(f)}}}function _(n){return!!(n[xi.oW]||n[xi.oH]||n.getClientRects()[xi.l])}function M(n){if(0===arguments[xi.l])return this;var t,r,e=new M,i=n,o=0;if(d(n)==gi)for(i=[],t="<"===n.charAt(0)?((r=hi.createElement("div")).innerHTML=n,r.children):hi.querySelectorAll(n);o<t[xi.l];o++)i.push(t[o]);if(i){for(d(i)==gi||m(i)&&i!==vi&&i!==i.self||(i=[i]),o=0;o<i[xi.l];o++)e[o]=i[o];e[xi.l]=i[xi.l]}return e}var O,S,ki,z,C,D,F,P,j,B,Q,U,V,$,Ii,Ti=(O=[],S="__overlayScrollbars__",function(n,t){var r=arguments[xi.l];if(r<1)return O;if(t)n[S]=t,O.push(n);else{var e=Oi.inA(n,O);if(-1<e){if(!(1<r))return O[e][S];delete n[S],O.splice(e,1)}}}),q=($=[],D=Oi.type,U={className:["os-theme-dark",[n,gi]],resize:["none","n:none b:both h:horizontal v:vertical"],sizeAutoCapable:P=[!0,wi],clipAlways:P,normalizeRTL:P,paddingAbsolute:j=[!(F=[wi,yi,gi,mi,pi,bi,n]),wi],autoUpdate:[null,[n,wi]],autoUpdateInterval:[33,yi],updateOnLoad:[["img"],[gi,mi,n]],nativeScrollbarsOverlaid:{showNativeScrollbars:j,initialize:P},overflowBehavior:{x:["scroll",Q="v-h:visible-hidden v-s:visible-scroll s:scroll h:hidden"],y:["scroll",Q]},scrollbars:{visibility:["auto","v:visible h:hidden a:auto"],autoHide:["never","n:never s:scroll l:leave m:move"],autoHideDelay:[800,yi],dragScrolling:P,clickScrolling:j,touchSupport:P,snapHandle:j},textarea:{dynWidth:j,dynHeight:j,inheritedAttrs:[["style","class"],[gi,mi,n]]},callbacks:{onInitialized:B=[null,[n,bi]],onInitializationWithdrawn:B,onDestroyed:B,onScrollStart:B,onScroll:B,onScrollStop:B,onOverflowChanged:B,onOverflowAmountChanged:B,onDirectionChanged:B,onContentSizeChanged:B,onHostSizeChanged:B,onUpdated:B}},Ii={g:(V=function(i){var o=function(n){var t,r,e;for(t in n)n[xi.hOP](t)&&(r=n[t],(e=D(r))==mi?n[t]=r[i?1:0]:e==pi&&(n[t]=o(r)));return n};return o(Ci.extend(!0,{},U))})(),_:V(!0),O:function(n,t,I,r){var e={},i={},o=Ci.extend(!0,{},n),T=Ci.inArray,A=Ci.isEmptyObject,H=function(n,t,r,e,i,o){for(var u in t)if(t[xi.hOP](u)&&n[xi.hOP](u)){var f,a,c,s,l,v,h,d,p=!1,b=!1,m=t[u],g=D(m),w=g==pi,y=Oi.isA(m)?m:[m],x=r[u],_=n[u],O=D(_),S=o?o+".":"",z='The option "'+S+u+"\" wasn't set, because",C=[],k=[];if(x=x===di?{}:x,w&&O==pi)e[u]={},i[u]={},H(_,m,x,e[u],i[u],S+u),Ci.each([n,e,i],function(n,t){A(t[u])&&delete t[u]});else if(!w){for(v=0;v<y[xi.l];v++)if(l=y[v],c=(g=D(l))==gi&&-1===T(l,F))for(C.push(gi),f=l.split(" "),k=k.concat(f),h=0;h<f[xi.l];h++){for(s=(a=f[h].split(":"))[0],d=0;d<a[xi.l];d++)if(_===a[d]){p=!0;break}if(p)break}else if(C.push(l),O===l){p=!0;break}p?((b=_!==x)&&(e[u]=_),(c?T(x,a)<0:b)&&(i[u]=c?s:_)):I&&console.warn(z+" it doesn't accept the type [ "+O.toUpperCase()+' ] with the value of "'+_+'".\r\nAccepted types are: [ '+C.join(", ").toUpperCase()+" ]."+(0<k[length]?"\r\nValid strings are: [ "+k.join(", ").split(":").join(", ")+" ].":"")),delete n[u]}}};return H(o,t,r||{},e,i),!A(o)&&I&&console.warn("The following options are discarded due to invalidity:\r\n"+vi.JSON.stringify(o,null,2)),{S:e,z:i}}},(ki=vi.OverlayScrollbars=function(n,r,e){if(0===arguments[xi.l])return this;var i,t,o=[],u=Ci.isPlainObject(r);return n?(n=n[xi.l]!=di?n:[n[0]||n],X(),0<n[xi.l]&&(u?Ci.each(n,function(n,t){(i=t)!==di&&o.push(K(i,r,e,z,C))}):Ci.each(n,function(n,t){i=Ti(t),("!"===r&&ki.valid(i)||Oi.type(r)==bi&&r(t,i)||r===di)&&o.push(i)}),t=1===o[xi.l]?o[0]:o),t):u||!r?t:o}).globals=function(){X();var n=Ci.extend(!0,{},z);return delete n.msie,n},ki.defaultOptions=function(n){X();var t=z.defaultOptions;if(n===di)return Ci.extend(!0,{},t);z.defaultOptions=Ci.extend(!0,{},t,Ii.O(n,Ii._,!0,t).S)},ki.valid=function(n){return n instanceof ki&&!n.getState().destroyed},ki.extension=function(n,t,r){var e=Oi.type(n)==gi,i=arguments[xi.l],o=0;if(i<1||!e)return Ci.extend(!0,{length:$[xi.l]},$);if(e)if(Oi.type(t)==bi)$.push({name:n,extensionFactory:t,defaultOptions:r});else for(;o<$[xi.l];o++)if($[o].name===n){if(!(1<i))return Ci.extend(!0,{},$[o]);$.splice(o,1)}},ki);function X(){z=z||new Y(Ii.g),C=C||new G(z)}function Y(n){var _=this,i="overflow",O=Ci("body"),S=Ci('<div id="os-dummy-scrollbar-size"><div></div></div>'),o=S[0],e=Ci(S.children("div").eq(0));O.append(S),S.hide().show();var t,r,u,f,a,c,s,l,v,h=z(o),d={x:0===h.x,y:0===h.y},p=(r=vi.navigator.userAgent,f="substring",a=r[u="indexOf"]("MSIE "),c=r[u]("Trident/"),s=r[u]("Edge/"),l=r[u]("rv:"),v=parseInt,0<a?t=v(r[f](a+5,r[u](".",a)),10):0<c?t=v(r[f](l+3,r[u](".",l)),10):0<s&&(t=v(r[f](s+5,r[u](".",s)),10)),t);function z(n){return{x:n[xi.oH]-n[xi.cH],y:n[xi.oW]-n[xi.cW]}}Ci.extend(_,{defaultOptions:n,msie:p,autoUpdateLoop:!1,autoUpdateRecommended:!Oi.mO(),nativeScrollbarSize:h,nativeScrollbarIsOverlaid:d,nativeScrollbarStyling:function(){var n=!1;S.addClass("os-viewport-native-scrollbars-invisible");try{n="none"===S.css("scrollbar-width")&&(9<p||!p)||"none"===vi.getComputedStyle(o,"::-webkit-scrollbar").getPropertyValue("display")}catch(t){}return n}(),overlayScrollbarDummySize:{x:30,y:30},cssCalc:_i.d("width","calc","(1px)")||null,restrictedMeasuring:function(){S.css(i,"hidden");var n=o[xi.sW],t=o[xi.sH];S.css(i,"visible");var r=o[xi.sW],e=o[xi.sH];return n-r!=0||t-e!=0}(),rtlScrollBehavior:function(){S.css({"overflow-y":"hidden","overflow-x":"scroll",direction:"rtl"}).scrollLeft(0);var n=S.offset(),t=e.offset();S.scrollLeft(-999);var r=e.offset();return{i:n.left===t.left,n:t.left!==r.left}}(),supportTransform:!!_i.v("transform"),supportTransition:!!_i.v("transition"),supportPassiveEvents:function(){var n=!1;try{vi.addEventListener("test",null,Object.defineProperty({},"passive",{get:function(){n=!0}}))}catch(t){}return n}(),supportResizeObserver:!!Oi.rO(),supportMutationObserver:!!Oi.mO()}),S.removeAttr(xi.s).remove(),function(){if(!d.x||!d.y){var m=Si.abs,g=Oi.wW(),w=Oi.wH(),y=x();Ci(vi).on("resize",function(){if(0<Ti().length){var n=Oi.wW(),t=Oi.wH(),r=n-g,e=t-w;if(0==r&&0==e)return;var i,o=Si.round(n/(g/100)),u=Si.round(t/(w/100)),f=m(r),a=m(e),c=m(o),s=m(u),l=x(),v=2<f&&2<a,h=!function b(n,t){var r=m(n),e=m(t);return r!==e&&r+1!==e&&r-1!==e}(c,s),d=v&&h&&(l!==y&&0<y),p=_.nativeScrollbarSize;d&&(O.append(S),i=_.nativeScrollbarSize=z(S[0]),S.remove(),p.x===i.x&&p.y===i.y||Ci.each(Ti(),function(){Ti(this)&&Ti(this).update("zoom")})),g=n,w=t,y=l}})}function x(){var n=vi.screen.deviceXDPI||0,t=vi.screen.logicalXDPI||1;return vi.devicePixelRatio||n/t}}()}function G(r){var c,e=Ci.inArray,s=Oi.now,l="autoUpdate",v=xi.l,h=[],d=[],p=!1,b=33,m=s(),g=function(){if(0<h[v]&&p){c=Oi.rAF()(function(){g()});var n,t,r,e,i,o,u=s(),f=u-m;if(b<f){m=u-f%b,n=33;for(var a=0;a<h[v];a++)(t=h[a])!==di&&(e=(r=t.options())[l],i=Si.max(1,r.autoUpdateInterval),o=s(),(!0===e||null===e)&&o-d[a]>i&&(t.update("auto"),d[a]=new Date(o+=i)),n=Si.max(1,Si.min(n,i)));b=n}}else b=33};this.add=function(n){-1===e(n,h)&&(h.push(n),d.push(s()),0<h[v]&&!p&&(p=!0,r.autoUpdateLoop=p,g()))},this.remove=function(n){var t=e(n,h);-1<t&&(d.splice(t,1),h.splice(t,1),0===h[v]&&p&&(p=!1,r.autoUpdateLoop=p,c!==di&&(Oi.cAF()(c),c=-1)))}}function K(r,n,t,xt,_t){var cn=Oi.type,sn=Ci.inArray,h=Ci.each,Ot=new ki,e=Ci[xi.p];if(ht(r)){if(Ti(r)){var i=Ti(r);return i.options(n),i}var St,zt,Ct,kt,D,It,Tt,At,F,ln,w,T,d,Ht,Et,Lt,Rt,y,p,Nt,Wt,Mt,Dt,Ft,Pt,jt,Bt,Qt,Ut,o,u,Vt,$t,qt,f,P,c,j,Xt,Yt,Gt,Kt,Jt,Zt,nr,tr,rr,er,ir,a,s,l,v,b,m,x,A,or,ur,fr,H,ar,cr,sr,lr,vr,hr,dr,pr,br,mr,gr,wr,yr,xr,_r,E,Or,Sr,zr,Cr,kr,Ir,Tr,Ar,g,_,Hr,Er,Lr,Rr,Nr,Wr,Mr,Dr,Fr,Pr,jr,Br,Qr,Ur,O,S,z,C,Vr,$r,k,I,qr,Xr,Yr,Gr,Kr,B,Q,Jr,Zr,ne,te,re={},vn={},hn={},ee={},ie={},L="-hidden",oe="margin-",ue="padding-",fe="border-",ae="top",ce="right",se="bottom",le="left",ve="min-",he="max-",de="width",pe="height",be="float",me="",ge="auto",dn="sync",we="scroll",ye="100%",pn="x",bn="y",R=".",xe=" ",N="scrollbar",W="-horizontal",M="-vertical",_e=we+"Left",Oe=we+"Top",U="mousedown touchstart",V="mouseup touchend touchcancel",$="mousemove touchmove",q="mouseenter",X="mouseleave",Y="keydown",G="keyup",K="selectstart",J="transitionend webkitTransitionEnd oTransitionEnd",Z="__overlayScrollbarsRO__",nn="os-",tn="os-html",rn="os-host",en=rn+"-foreign",on=rn+"-textarea",un=rn+"-"+N+W+L,fn=rn+"-"+N+M+L,an=rn+"-transition",Se=rn+"-rtl",ze=rn+"-resize-disabled",Ce=rn+"-scrolling",ke=rn+"-overflow",Ie=(ke=rn+"-overflow")+"-x",Te=ke+"-y",mn="os-textarea",gn=mn+"-cover",wn="os-padding",yn="os-viewport",Ae=yn+"-native-scrollbars-invisible",xn=yn+"-native-scrollbars-overlaid",_n="os-content",He="os-content-arrange",Ee="os-content-glue",Le="os-size-auto-observer",On="os-resize-observer",Sn="os-resize-observer-item",zn=Sn+"-final",Cn="os-text-inherit",kn=nn+N,In=kn+"-track",Tn=In+"-off",An=kn+"-handle",Hn=An+"-off",En=kn+"-unusable",Ln=kn+"-"+ge+L,Rn=kn+"-corner",Re=Rn+"-resize",Ne=Re+"-both",We=Re+W,Me=Re+M,Nn=kn+W,Wn=kn+M,Mn="os-dragging",De="os-theme-none",Dn=[Ae,xn,Tn,Hn,En,Ln,Re,Ne,We,Me,Mn].join(xe),Fn=[],Pn=[xi.ti],jn={},Fe={},Pe=42,Bn="load",Qn=[],Un={},Vn=["wrap","cols","rows"],$n=[xi.i,xi.c,xi.s,"open"].concat(Pn),qn=[];return Ot.sleep=function(){Ut=!0},Ot.update=function(n){var t,r,e,i,o;if(!Et)return cn(n)==gi?n===ge?(t=function u(){if(!Ut&&!Vr){var r,e,i,o=[],n=[{C:Yt,k:$n.concat(":visible")},{C:Lt?Xt:di,k:Vn}];return h(n,function(n,t){(r=t.C)&&h(t.k,function(n,t){e=":"===t.charAt(0)?r.is(t):r.attr(t),i=Un[t],fi(e,i)&&o.push(t),Un[t]=e})}),it(o),0<o[xi.l]}}(),r=function a(){if(Ut)return!1;var n,t,r,e,i=oi(),o=Lt&&br&&!Fr?Xt.val().length:0,u=!Vr&&br&&!Lt,f={};return u&&(n=nr.css(be),f[be]=Qt?ce:le,f[de]=ge,nr.css(f)),e={w:i[xi.sW]+o,h:i[xi.sH]+o},u&&(f[be]=n,f[de]=ye,nr.css(f)),t=Ve(),r=fi(e,g),g=e,r||t}(),(e=t||r)&&qe({I:r,T:Ht?di:Vt})):n===dn?Vr?(i=z(O.takeRecords()),o=C(S.takeRecords())):i=Ot.update(ge):"zoom"===n&&qe({A:!0,I:!0}):(n=Ut||n,Ut=!1,Ot.update(dn)&&!n||qe({H:n})),Xe(),e||i||o},Ot.options=function(n,t){var r,e={};if(Ci.isEmptyObject(n)||!Ci.isPlainObject(n)){if(cn(n)!=gi)return u;if(!(1<arguments.length))return bt(u,n);!function a(n,t,r){for(var e=t.split(R),i=e.length,o=0,u={},f=u;o<i;o++)u=u[e[o]]=o+1<i?{}:r;Ci.extend(n,f,!0)}(e,n,t),r=ot(e)}else r=ot(n);Ci.isEmptyObject(r)||qe({T:r})},Ot.destroy=function(){if(!Et){for(var n in _t.remove(Ot),Qe(),je(Kt),je(Gt),jn)Ot.removeExt(n);for(;0<qn[xi.l];)qn.pop()();Ue(!0),rr&&gt(rr),tr&&gt(tr),Wt&&gt(Gt),at(!0),st(!0),ut(!0);for(var t=0;t<Qn[xi.l];t++)Ci(Qn[t]).off(Bn,rt);Qn=di,Ut=Et=!0,Ti(r,0),ti("onDestroyed")}},Ot.scroll=function(n,t,r,e){if(0===arguments.length||n===di){var i=Wr&&Qt&&Ct.i,o=Wr&&Qt&&Ct.n,u=vn.L,f=vn.R,a=vn.N;return f=i?1-f:f,u=i?a-u:u,a*=o?-1:1,{position:{x:u*=o?-1:1,y:hn.L},ratio:{x:f,y:hn.R},max:{x:a,y:hn.N},handleOffset:{x:vn.W,y:hn.W},handleLength:{x:vn.M,y:hn.M},handleLengthRatio:{x:vn.D,y:hn.D},trackLength:{x:vn.F,y:hn.F},snappedHandleOffset:{x:vn.P,y:hn.P},isRTL:Qt,isRTLNormalized:Wr}}Ot.update(dn);var c,s,l,v,h,g,w,d,p,y=Wr,b=[pn,le,"l"],m=[bn,ae,"t"],x=["+=","-=","*=","/="],_=cn(t)==pi,O=_?t.complete:e,S={},z={},C="begin",k="nearest",I="never",T="ifneeded",A=xi.l,H=[pn,bn,"xy","yx"],E=[C,"end","center",k],L=["always",I,T],R=n[xi.hOP]("el"),N=R?n.el:n,W=!!(N instanceof Ci||zi)&&N instanceof zi,M=!W&&ht(N),D=function(){s&&Je(!0),l&&Je(!1)},F=cn(O)!=bi?di:function(){D(),O()};function P(n,t){for(c=0;c<t[A];c++)if(n===t[c])return 1}function j(n,t){var r=n?b:m;if(t=cn(t)==gi||cn(t)==yi?[t,t]:t,Oi.isA(t))return n?t[0]:t[1];if(cn(t)==pi)for(c=0;c<r[A];c++)if(r[c]in t)return t[r[c]]}function B(n,t){var r,e,i,o,u=cn(t)==gi,f=n?vn:hn,a=f.L,c=f.N,s=Qt&&n,l=s&&Ct.n&&!y,v="replace",h=eval;if((e=u?(2<t[A]&&(o=t.substr(0,2),-1<sn(o,x)&&(r=o)),t=(t=r?t.substr(2):t)[v](/min/g,0)[v](/</g,0)[v](/max/g,(l?"-":me)+ye)[v](/>/g,(l?"-":me)+ye)[v](/px/g,me)[v](/%/g," * "+c*(s&&Ct.n?-1:1)/100)[v](/vw/g," * "+ee.w)[v](/vh/g," * "+ee.h),ii(isNaN(t)?ii(h(t),!0).toFixed():t)):t)!==di&&!isNaN(e)&&cn(e)==yi){var d=y&&s,p=a*(d&&Ct.n?-1:1),b=d&&Ct.i,m=d&&Ct.n;switch(p=b?c-p:p,r){case"+=":i=p+e;break;case"-=":i=p-e;break;case"*=":i=p*e;break;case"/=":i=p/e;break;default:i=e}i=b?c-i:i,i*=m?-1:1,i=s&&Ct.n?Si.min(0,Si.max(c,i)):Si.max(0,Si.min(c,i))}return i===a?di:i}function Q(n,t,r,e){var i,o,u=[r,r],f=cn(n);if(f==t)n=[n,n];else if(f==mi){if(2<(i=n[A])||i<1)n=u;else for(1===i&&(n[1]=r),c=0;c<i;c++)if(o=n[c],cn(o)!=t||!P(o,e)){n=u;break}}else n=f==pi?[n[pn]||r,n[bn]||r]:u;return{x:n[0],y:n[1]}}function U(n){var t,r,e=[],i=[ae,ce,se,le];for(c=0;c<n[A]&&c!==i[A];c++)t=n[c],(r=cn(t))==wi?e.push(t?ii(p.css(oe+i[c])):0):e.push(r==yi?t:0);return e}if(W||M){var V,$=R?n.margin:0,q=R?n.axis:0,X=R?n.scroll:0,Y=R?n.block:0,G=[0,0,0,0],K=cn($);if(0<(p=W?N:Ci(N))[A]){$=K==yi||K==wi?U([$,$,$,$]):K==mi?2===(V=$[A])?U([$[0],$[1],$[0],$[1]]):4<=V?U($):G:K==pi?U([$[ae],$[ce],$[se],$[le]]):G,h=P(q,H)?q:"xy",g=Q(X,gi,"always",L),w=Q(Y,gi,C,E),d=$;var J=vn.L,Z=hn.L,nn=Jt.offset(),tn=p.offset(),rn={x:g.x==I||h==bn,y:g.y==I||h==pn};tn[ae]-=d[0],tn[le]-=d[3];var en={x:Si.round(tn[le]-nn[le]+J),y:Si.round(tn[ae]-nn[ae]+Z)};if(Qt&&(Ct.n||Ct.i||(en.x=Si.round(nn[le]-tn[le]+J)),Ct.n&&y&&(en.x*=-1),Ct.i&&y&&(en.x=Si.round(nn[le]-tn[le]+(vn.N-J)))),w.x!=C||w.y!=C||g.x==T||g.y==T||Qt){var on=p[0],un=ln?on[xi.bCR]():{width:on[xi.oW],height:on[xi.oH]},fn={w:un[de]+d[3]+d[1],h:un[pe]+d[0]+d[2]},an=function(n){var t=ni(n),r=t.j,e=t.B,i=t.Q,o=w[i]==(n&&Qt?C:"end"),u="center"==w[i],f=w[i]==k,a=g[i]==I,c=g[i]==T,s=ee[r],l=nn[e],v=fn[r],h=tn[e],d=u?2:1,p=h+v/2,b=l+s/2,m=v<=s&&l<=h&&h+v<=l+s;a?rn[i]=!0:rn[i]||((f||c)&&(rn[i]=c&&m,o=v<s?b<p:p<b),en[i]-=o||u?(s/d-v/d)*(n&&Qt&&y?-1:1):0)};an(!0),an(!1)}rn.y&&delete en.y,rn.x&&delete en.x,n=en}}S[_e]=B(!0,j(!0,n)),S[Oe]=B(!1,j(!1,n)),s=S[_e]!==di,l=S[Oe]!==di,(s||l)&&(0<t||_)?_?(t.complete=F,Zt.animate(S,t)):(v={duration:t,complete:F},Oi.isA(r)||Ci.isPlainObject(r)?(z[_e]=r[0]||r.x,z[Oe]=r[1]||r.y,v.specialEasing=z):v.easing=r,Zt.animate(S,v)):(s&&Zt[_e](S[_e]),l&&Zt[Oe](S[Oe]),D())},Ot.scrollStop=function(n,t,r){return Zt.stop(n,t,r),Ot},Ot.getElements=function(n){var t={target:or,host:ur,padding:ar,viewport:cr,content:sr,scrollbarHorizontal:{scrollbar:a[0],track:s[0],handle:l[0]},scrollbarVertical:{scrollbar:v[0],track:b[0],handle:m[0]},scrollbarCorner:ir[0]};return cn(n)==gi?bt(t,n):t},Ot.getState=function(n){function t(n){if(!Ci.isPlainObject(n))return n;var r=ai({},n),t=function(n,t){r[xi.hOP](n)&&(r[t]=r[n],delete r[n])};return t("w",de),t("h",pe),delete r.c,r}var r={destroyed:!!t(Et),sleeping:!!t(Ut),autoUpdate:t(!Vr),widthAuto:t(br),heightAuto:t(mr),padding:t(wr),overflowAmount:t(kr),hideOverflow:t(pr),hasOverflow:t(dr),contentScrollSize:t(vr),viewportSize:t(ee),hostSize:t(lr),documentMixed:t(y)};return cn(n)==gi?bt(r,n):r},Ot.ext=function(n){var t,r="added removed on contract".split(" "),e=0;if(cn(n)==gi){if(jn[xi.hOP](n))for(t=ai({},jn[n]);e<r.length;e++)delete t[r[e]]}else for(e in t={},jn)t[e]=ai({},Ot.ext(e));return t},Ot.addExt=function(n,t){var r,e,i,o,u=ki.extension(n),f=!0;if(u){if(jn[xi.hOP](n))return Ot.ext(n);if((r=u.extensionFactory.call(Ot,ai({},u.defaultOptions),Ci,Oi))&&(i=r.contract,cn(i)==bi&&(o=i(vi),f=cn(o)==wi?o:f),f))return e=(jn[n]=r).added,cn(e)==bi&&e(t),Ot.ext(n)}else console.warn('A extension with the name "'+n+"\" isn't registered.")},Ot.removeExt=function(n){var t,r=jn[n];return!!r&&(delete jn[n],t=r.removed,cn(t)==bi&&t(),!0)},ki.valid(function yt(n,t,r){var e,i;return o=xt.defaultOptions,It=xt.nativeScrollbarStyling,At=ai({},xt.nativeScrollbarSize),St=ai({},xt.nativeScrollbarIsOverlaid),zt=ai({},xt.overlayScrollbarDummySize),Ct=ai({},xt.rtlScrollBehavior),ot(ai({},o,t)),Tt=xt.cssCalc,D=xt.msie,kt=xt.autoUpdateRecommended,F=xt.supportTransition,ln=xt.supportTransform,w=xt.supportPassiveEvents,T=xt.supportResizeObserver,d=xt.supportMutationObserver,xt.restrictedMeasuring,P=Ci(n.ownerDocument),A=P[0],f=Ci(A.defaultView||A.parentWindow),x=f[0],c=wt(P,"html"),j=wt(c,"body"),Xt=Ci(n),or=Xt[0],Lt=Xt.is("textarea"),Rt=Xt.is("body"),y=A!==hi,p=Lt?Xt.hasClass(mn)&&Xt.parent().hasClass(_n):Xt.hasClass(rn)&&Xt.children(R+wn)[xi.l],St.x&&St.y&&!Vt.nativeScrollbarsOverlaid.initialize?(Ht=!0,ti("onInitializationWithdrawn"),p&&(ut(!0),at(!0),st(!0)),Ut=Et=!(Ht=!1)):(Rt&&((e={}).l=Si.max(Xt[_e](),c[_e](),f[_e]()),e.t=Si.max(Xt[Oe](),c[Oe](),f[Oe]()),i=function(){Zt.removeAttr(xi.ti),Xn(Zt,U,i,!0,!0)}),ut(),at(),st(),ft(),ct(!0),ct(!1),function s(){var r,t=x.top!==x,e={},i={},o={};function u(n){if(a(n)){var t=c(n),r={};(ne||Zr)&&(r[de]=i.w+(t.x-e.x)*o.x),(te||Zr)&&(r[pe]=i.h+(t.y-e.y)*o.y),Yt.css(r),Oi.stpP(n)}else f(n)}function f(n){var t=n!==di;Xn(P,[K,$,V],[tt,u,f],!0),si(j,Mn),ir.releaseCapture&&ir.releaseCapture(),t&&(r&&Be(),Ot.update(ge)),r=!1}function a(n){var t=(n.originalEvent||n).touches!==di;return!Ut&&!Et&&(1===Oi.mBtn(n)||t)}function c(n){return D&&t?{x:n.screenX,y:n.screenY}:Oi.page(n)}Yn(ir,U,function(n){a(n)&&!Jr&&(Vr&&(r=!0,Qe()),e=c(n),i.w=ur[xi.oW]-(Nt?0:Mt),i.h=ur[xi.oH]-(Nt?0:Dt),o=vt(),Xn(P,[K,$,V],[tt,u,f]),ci(j,Mn),ir.setCapture&&ir.setCapture(),Oi.prvD(n),Oi.stpP(n))})}(),Gn(),je(Kt,Kn),Rt&&(Zt[_e](e.l)[Oe](e.t),hi.activeElement==n&&cr.focus&&(Zt.attr(xi.ti,"-1"),cr.focus(),Xn(Zt,U,i,!1,!0))),Ot.update(ge),Ht=!0,ti("onInitialized"),h(Fn,function(n,t){ti(t.n,t.a)}),Fn=[],cn(r)==gi&&(r=[r]),Oi.isA(r)?h(r,function(n,t){Ot.addExt(t)}):Ci.isPlainObject(r)&&h(r,function(n,t){Ot.addExt(n,t)}),setTimeout(function(){F&&!Et&&ci(Yt,an)},333)),Ot}(r,n,t))&&Ti(r,Ot),Ot}function Xn(n,t,r,e,i){var o=Oi.isA(t)&&Oi.isA(r),u=e?"removeEventListener":"addEventListener",f=e?"off":"on",a=!o&&t.split(xe),c=0,s=Ci.isPlainObject(i),l=w&&(s?i.U:i)||!1,v=s&&(i.V||!1),h=w?{passive:l,capture:v}:v;if(o)for(;c<t[xi.l];c++)Xn(n,t[c],r[c],e,i);else for(;c<a[xi.l];c++)w?n[0][u](a[c],r,h):n[f](a[c],r)}function Yn(n,t,r,e){Xn(n,t,r,!1,e),qn.push(Oi.bind(Xn,0,n,t,r,!0,e))}function je(n,t){if(n){var r=Oi.rO(),e="animationstart mozAnimationStart webkitAnimationStart MSAnimationStart",i="childNodes",o=3333333,u=function(){n[Oe](o)[_e](Qt?Ct.n?-o:Ct.i?0:o:o),t()};if(t){if(T)((k=n.addClass("observed").append(ui(On)).contents()[0])[Z]=new r(u)).observe(k);else if(9<D||!kt){n.prepend(ui(On,ui({c:Sn,dir:"ltr"},ui(Sn,ui(zn))+ui(Sn,ui({c:zn,style:"width: 200%; height: 200%"})))));var f,a,c,s,l=n[0][i][0][i][0],v=Ci(l[i][1]),h=Ci(l[i][0]),d=Ci(h[0][i][0]),p=l[xi.oW],b=l[xi.oH],m=xt.nativeScrollbarSize,g=function(){h[_e](o)[Oe](o),v[_e](o)[Oe](o)},w=function(){a=0,f&&(p=c,b=s,u())},y=function(n){return c=l[xi.oW],s=l[xi.oH],f=c!=p||s!=b,n&&f&&!a?(Oi.cAF()(a),a=Oi.rAF()(w)):n||w(),g(),n&&(Oi.prvD(n),Oi.stpP(n)),!1},x={},_={};ri(_,me,[-2*(m.y+1),-2*m.x,-2*m.y,-2*(m.x+1)]),Ci(l).css(_),h.on(we,y),v.on(we,y),n.on(e,function(){y(!1)}),x[de]=o,x[pe]=o,d.css(x),g()}else{var O=A.attachEvent,S=D!==di;if(O)n.prepend(ui(On)),wt(n,R+On)[0].attachEvent("onresize",u);else{var z=A.createElement(pi);z.setAttribute(xi.ti,"-1"),z.setAttribute(xi.c,On),z.onload=function(){var n=this.contentDocument.defaultView;n.addEventListener("resize",u),n.document.documentElement.style.display="none"},z.type="text/html",S&&n.prepend(z),z.data="about:blank",S||n.prepend(z),n.on(e,u)}}if(n[0]===H){var C=function(){var n=Yt.css("direction"),t={},r=0,e=!1;return n!==E&&(r="ltr"===n?(t[le]=0,t[ce]=ge,o):(t[le]=ge,t[ce]=0,Ct.n?-o:Ct.i?0:o),Kt.children().eq(0).css(t),Kt[_e](r)[Oe](o),E=n,e=!0),e};C(),Yn(n,we,function(n){return C()&&qe(),Oi.prvD(n),Oi.stpP(n),!1})}}else if(T){var k,I=(k=n.contents()[0])[Z];I&&(I.disconnect(),delete k[Z])}else gt(n.children(R+On).eq(0))}}function Gn(){if(d){var o,u,f,a,c,s,r,e,i,l,n=Oi.mO(),v=Oi.now();C=function(n){var t=!1;return Ht&&!Ut&&(h(n,function(){return!(t=function o(n){var t=n.attributeName,r=n.target,e=n.type,i="closest";if(r===sr)return null===t;if("attributes"===e&&(t===xi.c||t===xi.s)&&!Lt){if(t===xi.c&&Ci(r).hasClass(rn))return et(n.oldValue,r.className);if(typeof r[i]!=bi)return!0;if(null!==r[i](R+On)||null!==r[i](R+kn)||null!==r[i](R+Rn))return!1}return!0}(this))}),t&&(e=Oi.now(),i=mr||br,l=function(){Et||(v=e,Lt&&$e(),i?qe():Ot.update(ge))},clearTimeout(r),11<e-v||!i?l():r=setTimeout(l,11))),t},O=new n(z=function(n){var t,r=!1,e=!1,i=[];return Ht&&!Ut&&(h(n,function(){o=(t=this).target,u=t.attributeName,f=u===xi.c,a=t.oldValue,c=o.className,p&&f&&!e&&-1<a.indexOf(en)&&c.indexOf(en)<0&&(s=lt(!0),ur.className=c.split(xe).concat(a.split(xe).filter(function(n){return n.match(s)})).join(xe),r=e=!0),r=r||(f?et(a,c):u!==xi.s||a!==o[xi.s].cssText),i.push(u)}),it(i),r&&Ot.update(e||ge)),r}),S=new n(C)}}function Be(){d&&!Vr&&(O.observe(ur,{attributes:!0,attributeOldValue:!0,attributeFilter:$n}),S.observe(Lt?or:sr,{attributes:!0,attributeOldValue:!0,subtree:!Lt,childList:!Lt,characterData:!Lt,attributeFilter:Lt?Vn:$n}),Vr=!0)}function Qe(){d&&Vr&&(O.disconnect(),S.disconnect(),Vr=!1)}function Kn(){if(!Ut){var n,t={w:H[xi.sW],h:H[xi.sH]};n=fi(t,_),_=t,n&&qe({A:!0})}}function Jn(){Kr&&Ge(!0)}function Zn(){Kr&&!j.hasClass(Mn)&&Ge(!1)}function nt(){Gr&&(Ge(!0),clearTimeout(I),I=setTimeout(function(){Gr&&!Et&&Ge(!1)},100))}function tt(n){return Oi.prvD(n),!1}function rt(n){if(!Et){var t=n.target,r=Ci(n.target),e=Ci.inArray(t,Qn);-1<e&&Qn.splice(e,1),mt(function(n,t){r.is(t)&&qe({I:!0})})}}function Ue(n){n||Ue(!0),Xn(Yt,$.split(xe)[0],nt,!Gr||n,!0),Xn(Yt,[q,X],[Jn,Zn],!Kr||n,!0),Ht||n||Yt.one("mouseover",Jn)}function Ve(){var n={};return Rt&&tr&&(n.w=ii(tr.css(ve+de)),n.h=ii(tr.css(ve+pe)),n.c=fi(n,Ur),n.f=!0),!!(Ur=n).c}function et(n,t){var r,e,i=typeof t==gi?t.split(xe):[],o=function f(n,t){var r,e,i=[],o=[];for(r=0;r<n.length;r++)i[n[r]]=!0;for(r=0;r<t.length;r++)i[t[r]]?delete i[t[r]]:i[t[r]]=!0;for(e in i)o.push(e);return o}(typeof n==gi?n.split(xe):[],i),u=sn(De,o);if(-1<u&&o.splice(u,1),0<o[xi.l])for(e=lt(!0,!0),r=0;r<o.length;r++)if(!o[r].match(e))return!0;return!1}function it(n){h(n=n||Pn,function(n,t){if(-1<Oi.inA(t,Pn)){var r=Xt.attr(t);cn(r)==gi?Zt.attr(t,r):Zt.removeAttr(t)}})}function $e(){if(!Ut){var n,t,r,e,i=!Fr,o=ee.w,u=ee.h,f={},a=br||i;return f[ve+de]=me,f[ve+pe]=me,f[de]=ge,Xt.css(f),n=or[xi.oW],t=a?Si.max(n,or[xi.sW]-1):1,f[de]=br?ge:ye,f[ve+de]=ye,f[pe]=ge,Xt.css(f),r=or[xi.oH],e=Si.max(r,or[xi.sH]-1),f[de]=t,f[pe]=e,er.css(f),f[ve+de]=o,f[ve+pe]=u,Xt.css(f),{$:n,X:r,Y:t,G:e}}}function qe(n){clearTimeout(qt),n=n||{},Fe.A|=n.A,Fe.I|=n.I,Fe.H|=n.H;var t,r=Oi.now(),e=!!Fe.A,i=!!Fe.I,o=!!Fe.H,u=n.T,f=0<Pe&&Ht&&!Et&&!o&&!u&&r-$t<Pe&&!mr&&!br;if(f&&(qt=setTimeout(qe,Pe)),!(Et||f||Ut&&!u||Ht&&!o&&(t=Yt.is(":hidden"))||"inline"===Yt.css("display"))){$t=r,Fe={},!It||St.x&&St.y?At=ai({},xt.nativeScrollbarSize):(At.x=0,At.y=0),ie={x:3*(At.x+(St.x?0:3)),y:3*(At.y+(St.y?0:3))},u=u||{};var a=function(){return fi.apply(this,[].slice.call(arguments).concat([o]))},c={x:Zt[_e](),y:Zt[Oe]()},s=Vt.scrollbars,l=Vt.textarea,v=s.visibility,h=a(v,Hr),d=s.autoHide,p=a(d,Er),b=s.clickScrolling,m=a(b,Lr),g=s.dragScrolling,w=a(g,Rr),y=Vt.className,x=a(y,Mr),_=Vt.resize,O=a(_,Nr)&&!Rt,S=Vt.paddingAbsolute,z=a(S,Or),C=Vt.clipAlways,k=a(C,Sr),I=Vt.sizeAutoCapable&&!Rt,T=a(I,Ar),A=Vt.nativeScrollbarsOverlaid.showNativeScrollbars,H=a(A,Ir),E=Vt.autoUpdate,L=a(E,Tr),R=Vt.overflowBehavior,N=a(R,Cr,o),W=l.dynWidth,M=a(Qr,W),D=l.dynHeight,F=a(Br,D);if(Xr="n"===d,Yr="s"===d,Gr="m"===d,Kr="l"===d,qr=s.autoHideDelay,Dr=Mr,Jr="n"===_,Zr="b"===_,ne="h"===_,te="v"===_,Wr=Vt.normalizeRTL,A=A&&St.x&&St.y,Hr=v,Er=d,Lr=b,Rr=g,Mr=y,Nr=_,Or=S,Sr=C,Ar=I,Ir=A,Tr=E,Cr=ai({},R),Qr=W,Br=D,dr=dr||{x:!1,y:!1},x&&(si(Yt,Dr+xe+De),ci(Yt,y!==di&&null!==y&&0<y.length?y:De)),L&&(!0===E||null===E&&kt?(Qe(),_t.add(Ot)):(_t.remove(Ot),Be())),T)if(I)if(rr?rr.show():(rr=Ci(ui(Ee)),Jt.before(rr)),Wt)Gt.show();else{Gt=Ci(ui(Le)),fr=Gt[0],rr.before(Gt);var P={w:-1,h:-1};je(Gt,function(){var n={w:fr[xi.oW],h:fr[xi.oH]};fi(n,P)&&(Ht&&mr&&0<n.h||br&&0<n.w||Ht&&!mr&&0===n.h||!br&&0===n.w)&&qe(),P=n}),Wt=!0,null!==Tt&&Gt.css(pe,Tt+"(100% + 1px)")}else Wt&&Gt.hide(),rr&&rr.hide();o&&(Kt.find("*").trigger(we),Wt&&Gt.find("*").trigger(we)),t=t===di?Yt.is(":hidden"):t;var j,B=!!Lt&&"off"!==Xt.attr("wrap"),Q=a(B,Fr),U=Yt.css("direction"),V=a(U,_r),$=Yt.css("box-sizing"),q=a($,gr),X=ei(ue);try{j=Wt?fr[xi.bCR]():null}catch(wt){return}Nt="border-box"===$;var Y=(Qt="rtl"===U)?le:ce,G=Qt?ce:le,K=!1,J=!(!Wt||"none"===Yt.css(be))&&(0===Si.round(j.right-j.left)&&(!!S||0<ur[xi.cW]-Mt));if(I&&!J){var Z=ur[xi.oW],nn=rr.css(de);rr.css(de,ge);var tn=ur[xi.oW];rr.css(de,nn),(K=Z!==tn)||(rr.css(de,Z+1),tn=ur[xi.oW],rr.css(de,nn),K=Z!==tn)}var rn=(J||K)&&I&&!t,en=a(rn,br),on=!rn&&br,un=!(!Wt||!I||t)&&0===Si.round(j.bottom-j.top),fn=a(un,mr),an=!un&&mr,cn=ei(fe,"-"+de,!(rn&&Nt||!Nt),!(un&&Nt||!Nt)),sn=ei(oe),ln={},vn={},hn=function(){return{w:ur[xi.cW],h:ur[xi.cH]}},dn=function(){return{w:ar[xi.oW]+Si.max(0,sr[xi.cW]-sr[xi.sW]),h:ar[xi.oH]+Si.max(0,sr[xi.cH]-sr[xi.sH])}},pn=Mt=X.l+X.r,bn=Dt=X.t+X.b;if(pn*=S?1:0,bn*=S?1:0,X.c=a(X,wr),Ft=cn.l+cn.r,Pt=cn.t+cn.b,cn.c=a(cn,yr),jt=sn.l+sn.r,Bt=sn.t+sn.b,sn.c=a(sn,xr),Fr=B,_r=U,gr=$,br=rn,mr=un,wr=X,yr=cn,xr=sn,V&&Wt&&Gt.css(be,G),X.c||V||z||en||fn||q||T){var mn={},gn={},wn=[X.t,X.r,X.b,X.l];ri(vn,oe,[-X.t,-X.r,-X.b,-X.l]),S?(ri(mn,me,wn),ri(Lt?gn:ln,ue)):(ri(mn,me),ri(Lt?gn:ln,ue,wn)),Jt.css(mn),Xt.css(gn)}ee=dn();var yn=!!Lt&&$e(),xn=Lt&&a(yn,jr),_n=Lt&&yn?{w:W?yn.Y:yn.$,h:D?yn.G:yn.X}:{};if(jr=yn,un&&(fn||z||q||X.c||cn.c)?ln[pe]=ge:(fn||z)&&(ln[pe]=ye),rn&&(en||z||q||X.c||cn.c||V)?(ln[de]=ge,vn[he+de]=ye):(en||z)&&(ln[de]=ye,ln[be]=me,vn[he+de]=me),rn?(vn[de]=ge,ln[de]=_i.d(de,"max-content intrinsic")||ge,ln[be]=G):vn[de]=me,vn[pe]=un?_n.h||sr[xi.cH]:me,I&&rr.css(vn),nr.css(ln),ln={},vn={},e||i||xn||V||q||z||en||rn||fn||un||H||N||k||O||h||p||w||m||M||F||Q){var On="overflow",Sn=On+"-x",zn=On+"-y";if(!It){var Cn={},kn=dr.y&&pr.ys&&!A?St.y?Zt.css(Y):-At.y:0,In=dr.x&&pr.xs&&!A?St.x?Zt.css(se):-At.x:0;ri(Cn,me),Zt.css(Cn)}var Tn=oi(),An={w:_n.w||Tn[xi.cW],h:_n.h||Tn[xi.cH]},Hn=Tn[xi.sW],En=Tn[xi.sH];It||(Cn[se]=an?me:In,Cn[Y]=on?me:kn,Zt.css(Cn)),ee=dn();var Ln=hn(),Rn={w:Ln.w-jt-Ft-(Nt?0:Mt),h:Ln.h-Bt-Pt-(Nt?0:Dt)},Nn={w:Si.max((rn?An.w:Hn)+pn,Rn.w),h:Si.max((un?An.h:En)+bn,Rn.h)};if(Nn.c=a(Nn,zr),zr=Nn,I){(Nn.c||un||rn)&&(vn[de]=Nn.w,vn[pe]=Nn.h,Lt||(An={w:Tn[xi.cW],h:Tn[xi.cH]}));var Wn={},Mn=function(n){var t=ni(n),r=t.j,e=t.K,i=n?rn:un,o=n?Ft:Pt,u=n?Mt:Dt,f=n?jt:Bt,a=ee[r]-o-f-(Nt?0:u);i&&(i||!cn.c)||(vn[e]=Rn[r]-1),!(i&&An[r]<a)||n&&Lt&&B||(Lt&&(Wn[e]=ii(er.css(e))-1),--vn[e]),0<An[r]&&(vn[e]=Si.max(1,vn[e]))};Mn(!0),Mn(!1),Lt&&er.css(Wn),rr.css(vn)}rn&&(ln[de]=ye),!rn||Nt||Vr||(ln[be]="none"),nr.css(ln),ln={};var Dn={w:Tn[xi.sW],h:Tn[xi.sH]};Dn.c=i=a(Dn,vr),vr=Dn,ee=dn(),e=a(Ln=hn(),lr),lr=Ln;var Fn=Lt&&(0===ee.w||0===ee.h),Pn=kr,jn={},Bn={},Qn={},Un={},Vn={},$n={},qn={},Xn=ar[xi.bCR](),Yn=function(n){var t=ni(n),r=ni(!n).Q,e=t.Q,i=t.j,o=t.K,u=we+t.J+"Max",f=Xn[o]?Si.abs(Xn[o]-ee[i]):0,a=Pn&&0<Pn[e]&&0===cr[u];jn[e]="v-s"===R[e],Bn[e]="v-h"===R[e],Qn[e]="s"===R[e],Un[e]=Si.max(0,Si.round(100*(Dn[i]-ee[i]))/100),Un[e]*=Fn||a&&0<f&&f<1?0:1,Vn[e]=0<Un[e],$n[e]=jn[e]||Bn[e]?Vn[r]&&!jn[r]&&!Bn[r]:Vn[e],$n[e+"s"]=!!$n[e]&&(Qn[e]||jn[e]),qn[e]=Vn[e]&&$n[e+"s"]};if(Yn(!0),Yn(!1),Un.c=a(Un,kr),kr=Un,Vn.c=a(Vn,dr),dr=Vn,$n.c=a($n,pr),pr=$n,St.x||St.y){var Gn,Kn={},Jn={},Zn=o;(Vn.x||Vn.y)&&(Jn.w=St.y&&Vn.y?Dn.w+zt.y:me,Jn.h=St.x&&Vn.x?Dn.h+zt.x:me,Zn=a(Jn,hr),hr=Jn),(Vn.c||$n.c||Dn.c||V||en||fn||rn||un||H)&&(ln[oe+G]=ln[fe+G]=me,Gn=function(n){var t=ni(n),r=ni(!n),e=t.Q,i=n?se:Y,o=n?un:rn;St[e]&&Vn[e]&&$n[e+"s"]?(ln[oe+i]=!o||A?me:zt[e],ln[fe+i]=n&&o||A?me:zt[e]+"px solid transparent"):(Jn[r.j]=ln[oe+i]=ln[fe+i]=me,Zn=!0)},It?li(Zt,Ae,!A):(Gn(!0),Gn(!1))),A&&(Jn.w=Jn.h=me,Zn=!0),Zn&&!It&&(Kn[de]=$n.y?Jn.w:me,Kn[pe]=$n.x?Jn.h:me,tr||(tr=Ci(ui(He)),Zt.prepend(tr)),tr.css(Kn)),nr.css(ln)}var nt,tt={};mn={};if((e||Vn.c||$n.c||Dn.c||N||q||H||V||k||fn)&&(tt[G]=me,(nt=function(n){var t=ni(n),r=ni(!n),e=t.Q,i=t.Z,o=n?se:Y,u=function(){tt[o]=me,re[r.j]=0};Vn[e]&&$n[e+"s"]?(tt[On+i]=we,A||It?u():(tt[o]=-(St[e]?zt[e]:At[e]),re[r.j]=St[e]?zt[r.Q]:0)):(tt[On+i]=me,u())})(!0),nt(!1),!It&&(ee.h<ie.x||ee.w<ie.y)&&(Vn.x&&$n.x&&!St.x||Vn.y&&$n.y&&!St.y)?(tt[ue+ae]=ie.x,tt[oe+ae]=-ie.x,tt[ue+G]=ie.y,tt[oe+G]=-ie.y):tt[ue+ae]=tt[oe+ae]=tt[ue+G]=tt[oe+G]=me,tt[ue+Y]=tt[oe+Y]=me,Vn.x&&$n.x||Vn.y&&$n.y||Fn?Lt&&Fn&&(mn[Sn]=mn[zn]="hidden"):(!C||Bn.x||jn.x||Bn.y||jn.y)&&(Lt&&(mn[Sn]=mn[zn]=me),tt[Sn]=tt[zn]="visible"),Jt.css(mn),Zt.css(tt),tt={},(Vn.c||q||en||fn)&&(!St.x||!St.y))){var rt=sr[xi.s];rt.webkitTransform="scale(1)",rt.display="run-in",sr[xi.oH],rt.display=me,rt.webkitTransform=me}if(ln={},V||en||fn)if(Qt&&rn){var et=nr.css(be),it=Si.round(nr.css(be,me).css(le,me).position().left);nr.css(be,et),it!==Si.round(nr.position().left)&&(ln[le]=it)}else ln[le]=me;if(nr.css(ln),Lt&&i){var ot=function yt(){var n=or.selectionStart;if(n===di)return;var t,r,e=Xt.val(),i=e[xi.l],o=e.split("\n"),u=o[xi.l],f=e.substr(0,n).split("\n"),a=0,c=0,s=f[xi.l],l=f[f[xi.l]-1][xi.l];for(r=0;r<o[xi.l];r++)t=o[r][xi.l],c<t&&(a=r+1,c=t);return{nn:s,tn:l,rn:u,en:c,"in":a,un:n,an:i}}();if(ot){var ut=Pr===di||ot.rn!==Pr.rn,ft=ot.nn,at=ot.tn,ct=ot["in"],st=ot.rn,lt=ot.en,vt=ot.un,ht=ot.an<=vt&&$r,dt={x:B||at!==lt||ft!==ct?-1:kr.x,y:(B?ht||ut&&Pn&&c.y===Pn.y:(ht||ut)&&ft===st)?kr.y:-1};c.x=-1<dt.x?Qt&&Wr&&Ct.i?0:dt.x:c.x,c.y=-1<dt.y?dt.y:c.y}Pr=ot}Qt&&Ct.i&&St.y&&Vn.x&&Wr&&(c.x+=re.w||0),rn&&Yt[_e](0),un&&Yt[Oe](0),Zt[_e](c.x)[Oe](c.y);var pt="v"===v,bt="h"===v,mt="a"===v,gt=function(n,t){t=t===di?n:t,Ye(!0,n,qn.x),Ye(!1,t,qn.y)};li(Yt,ke,$n.x||$n.y),li(Yt,Ie,$n.x),li(Yt,Te,$n.y),V&&!Rt&&li(Yt,Se,Qt),Rt&&ci(Yt,ze),O&&(li(Yt,ze,Jr),li(ir,Re,!Jr),li(ir,Ne,Zr),li(ir,We,ne),li(ir,Me,te)),(h||N||$n.c||Vn.c||H)&&(A?H&&(si(Yt,Ce),A&&gt(!1)):mt?gt(qn.x,qn.y):pt?gt(!0):bt&&gt(!1)),(p||H)&&(Ue(!Kr&&!Gr),Ge(Xr,!Xr)),(e||Un.c||fn||en||O||q||z||H||V)&&(Ke(!0),Je(!0),Ke(!1),Je(!1)),m&&Ze(!0,b),w&&Ze(!1,g),ti("onDirectionChanged",{isRTL:Qt,dir:U},V),ti("onHostSizeChanged",{width:lr.w,height:lr.h},e),ti("onContentSizeChanged",{width:vr.w,height:vr.h},i),ti("onOverflowChanged",{x:Vn.x,y:Vn.y,xScrollable:$n.xs,yScrollable:$n.ys,clipped:$n.x||$n.y},Vn.c||$n.c),ti("onOverflowAmountChanged",{x:Un.x,y:Un.y},Un.c)}Rt&&Ur&&(dr.c||Ur.c)&&(Ur.f||Ve(),St.y&&dr.x&&nr.css(ve+de,Ur.w+zt.y),St.x&&dr.y&&nr.css(ve+pe,Ur.h+zt.x),Ur.c=!1),Ht&&u.updateOnLoad&&Xe(),ti("onUpdated",{forced:o})}}function Xe(){Lt||mt(function(n,t){nr.find(t).each(function(n,t){Oi.inA(t,Qn)<0&&(Qn.push(t),Ci(t).off(Bn,rt).on(Bn,rt))})})}function ot(n){var t=Ii.O(n,Ii._,!0,u);return u=ai({},u,t.S),Vt=ai({},Vt,t.z),t.z}function ut(e){var n="parent",t=mn+xe+Cn,r=Lt?xe+Cn:me,i=Vt.textarea.inheritedAttrs,o={},u=function(){var r=e?Xt:Yt;h(o,function(n,t){cn(t)==gi&&(n==xi.c?r.addClass(t):r.attr(n,t))})},f=[rn,en,on,ze,Se,un,fn,an,Ce,ke,Ie,Te,De,mn,Cn,Mr].join(xe),a={};Yt=Yt||(Lt?p?Xt[n]()[n]()[n]()[n]():Ci(ui(on)):Xt),nr=nr||pt(_n+r),Zt=Zt||pt(yn+r),Jt=Jt||pt(wn+r),Kt=Kt||pt("os-resize-observer-host"),er=er||(Lt?pt(gn):di),p&&ci(Yt,en),e&&si(Yt,f),i=cn(i)==gi?i.split(xe):i,Oi.isA(i)&&Lt&&h(i,function(n,t){cn(t)==gi&&(o[t]=e?Yt.attr(t):Xt.attr(t))}),e?(p&&Ht?(Kt.children().remove(),h([Jt,Zt,nr,er],function(n,t){t&&si(t.removeAttr(xi.s),Dn)}),ci(Yt,Lt?on:rn)):(gt(Kt),nr.contents().unwrap().unwrap().unwrap(),Lt&&(Xt.unwrap(),gt(Yt),gt(er),u())),Lt&&Xt.removeAttr(xi.s),Rt&&si(c,tn)):(Lt&&(Vt.sizeAutoCapable||(a[de]=Xt.css(de),a[pe]=Xt.css(pe)),p||Xt.addClass(Cn).wrap(Yt),Yt=Xt[n]().css(a)),p||(ci(Xt,Lt?t:rn),Yt.wrapInner(nr).wrapInner(Zt).wrapInner(Jt).prepend(Kt),nr=wt(Yt,R+_n),Zt=wt(Yt,R+yn),Jt=wt(Yt,R+wn),Lt&&(nr.prepend(er),u())),It&&ci(Zt,Ae),St.x&&St.y&&ci(Zt,xn),Rt&&ci(c,tn),H=Kt[0],ur=Yt[0],ar=Jt[0],cr=Zt[0],sr=nr[0],it())}function ft(){var r,t,e=[112,113,114,115,116,117,118,119,120,121,123,33,34,37,38,39,40,16,17,18,19,20,144],i=[],n="focus";function o(n){$e(),Ot.update(ge),n&&kt&&clearInterval(r)}Lt?(9<D||!kt?Yn(Xt,"input",o):Yn(Xt,[Y,G],[function u(n){var t=n.keyCode;sn(t,e)<0&&(i[xi.l]||(o(),r=setInterval(o,1e3/60)),sn(t,i)<0&&i.push(t))},function f(n){var t=n.keyCode,r=sn(t,i);sn(t,e)<0&&(-1<r&&i.splice(r,1),i[xi.l]||o(!0))}]),Yn(Xt,[we,"drop",n,n+"out"],[function a(n){return Xt[_e](Ct.i&&Wr?9999999:0),Xt[Oe](0),Oi.prvD(n),Oi.stpP(n),!1},function c(n){setTimeout(function(){Et||o()},50)},function s(){$r=!0,ci(Yt,n)},function l(){$r=!1,i=[],si(Yt,n),o(!0)}])):Yn(nr,J,function v(n){!0!==Tr&&function l(n){if(!Ht)return 1;var t="flex-grow",r="flex-shrink",e="flex-basis",i=[de,ve+de,he+de,oe+le,oe+ce,le,ce,"font-weight","word-spacing",t,r,e],o=[ue+le,ue+ce,fe+le+de,fe+ce+de],u=[pe,ve+pe,he+pe,oe+ae,oe+se,ae,se,"line-height",t,r,e],f=[ue+ae,ue+se,fe+ae+de,fe+se+de],a="s"===Cr.x||"v-s"===Cr.x,c=!1,s=function(n,t){for(var r=0;r<n[xi.l];r++)if(n[r]===t)return!0;return!1};return("s"===Cr.y||"v-s"===Cr.y)&&((c=s(u,n))||Nt||(c=s(f,n))),a&&!c&&((c=s(i,n))||Nt||(c=s(o,n))),c}((n=n.originalEvent||n).propertyName)&&Ot.update(ge)}),Yn(Zt,we,function h(n){Ut||(t!==di?clearTimeout(t):((Yr||Gr)&&Ge(!0),dt()||ci(Yt,Ce),ti("onScrollStart",n)),Q||(Je(!0),Je(!1)),ti("onScroll",n),t=setTimeout(function(){Et||(clearTimeout(t),t=di,(Yr||Gr)&&Ge(!1),dt()||si(Yt,Ce),ti("onScrollStop",n))},175))},!0)}function at(i){var n,t,o=function(n){var t=pt(kn+xe+(n?Nn:Wn),!0),r=pt(In,t),e=pt(An,t);return p||i||(t.append(r),r.append(e)),{cn:t,sn:r,ln:e}};function r(n){var t=ni(n),r=t.cn,e=t.sn,i=t.ln;p&&Ht?h([r,e,i],function(n,t){si(t.removeAttr(xi.s),Dn)}):gt(r||o(n).cn)}i?(r(!0),r()):(n=o(!0),t=o(),a=n.cn,s=n.sn,l=n.ln,v=t.cn,b=t.sn,m=t.ln,p||(Jt.after(v),Jt.after(a)))}function ct(S){var z,i,C,k,e=ni(S),I=e.vn,t=x.top!==x,T=e.Q,r=e.Z,A=we+e.J,o="active",u="snapHandle",f="click",H=1,a=[16,17];function c(n){return D&&t?n["screen"+r]:Oi.page(n)[T]}function s(n){return Vt.scrollbars[n]}function l(){H=.5}function v(){H=1}function h(n){Oi.stpP(n)}function E(n){-1<sn(n.keyCode,a)&&l()}function L(n){-1<sn(n.keyCode,a)&&v()}function R(n){var t=(n.originalEvent||n).touches!==di;return!(Ut||Et||dt()||!Rr||t&&!s("touchSupport"))&&(1===Oi.mBtn(n)||t)}function d(n){if(R(n)){var t=I.F,r=I.M,e=I.N*((c(n)-C)*k/(t-r));e=isFinite(e)?e:0,Qt&&S&&!Ct.i&&(e*=-1),Zt[A](Si.round(i+e)),Q&&Je(S,i+e),w||Oi.prvD(n)}else N(n)}function N(n){if(n=n||n.originalEvent,Xn(P,[$,V,Y,G,K],[d,N,E,L,tt],!0),Oi.rAF()(function(){Xn(P,f,h,!0,{V:!0})}),Q&&Je(S,!0),Q=!1,si(j,Mn),si(e.ln,o),si(e.sn,o),si(e.cn,o),k=1,v(),z!==(C=i=di)&&(Ot.scrollStop(),clearTimeout(z),z=di),n){var t=ur[xi.bCR]();n.clientX>=t.left&&n.clientX<=t.right&&n.clientY>=t.top&&n.clientY<=t.bottom||Zn(),(Yr||Gr)&&Ge(!1)}}function W(n){i=Zt[A](),i=isNaN(i)?0:i,(Qt&&S&&!Ct.n||!Qt)&&(i=i<0?0:i),k=vt()[T],C=c(n),Q=!s(u),ci(j,Mn),ci(e.ln,o),ci(e.cn,o),Xn(P,[$,V,K],[d,N,tt]),Oi.rAF()(function(){Xn(P,f,h,!1,{V:!0})}),!D&&y||Oi.prvD(n),Oi.stpP(n)}Yn(e.ln,U,function p(n){R(n)&&W(n)}),Yn(e.sn,[U,q,X],[function M(n){if(R(n)){var h,t=e.vn.M/Math.round(Si.min(1,ee[e.j]/vr[e.j])*e.vn.F),d=Si.round(ee[e.j]*t),p=270*t,b=400*t,m=e.sn.offset()[e.B],r=n.ctrlKey,g=n.shiftKey,w=g&&r,y=!0,x=function(n){Q&&Je(S,n)},_=function(){x(),W(n)},O=function(){if(!Et){var n=(C-m)*k,t=I.W,r=I.F,e=I.M,i=I.N,o=I.L,u=p*H,f=y?Si.max(b,u):u,a=i*((n-e/2)/(r-e)),c=Qt&&S&&(!Ct.i&&!Ct.n||Wr),s=c?t<n:n<t,l={},v={easing:"linear",step:function(n){Q&&(Zt[A](n),Je(S,n))}};a=isFinite(a)?a:0,a=Qt&&S&&!Ct.i?i-a:a,g?(Zt[A](a),w?(a=Zt[A](),Zt[A](o),a=c&&Ct.i?i-a:a,a=c&&Ct.n?-a:a,l[T]=a,Ot.scroll(l,ai(v,{duration:130,complete:_}))):_()):(h=y?s:h,(c?h?n<=t+e:t<=n:h?t<=n:n<=t+e)?(clearTimeout(z),Ot.scrollStop(),z=di,x(!0)):(z=setTimeout(O,f),l[T]=(h?"-=":"+=")+d,Ot.scroll(l,ai(v,{duration:u}))),y=!1)}};r&&l(),k=vt()[T],C=Oi.page(n)[T],Q=!s(u),ci(j,Mn),ci(e.sn,o),ci(e.cn,o),Xn(P,[V,Y,G,K],[N,E,L,tt]),O(),Oi.prvD(n),Oi.stpP(n)}},function b(n){B=!0,(Yr||Gr)&&Ge(!0)},function m(n){B=!1,(Yr||Gr)&&Ge(!1)}]),Yn(e.cn,U,function g(n){Oi.stpP(n)}),F&&Yn(e.cn,J,function(n){n.target===e.cn[0]&&(Ke(S),Je(S))})}function Ye(n,t,r){var e=n?a:v;li(Yt,n?un:fn,!t),li(e,En,!r)}function Ge(n,t){if(clearTimeout(k),n)si(a,Ln),si(v,Ln);else{var r,e=function(){B||Et||(!(r=l.hasClass("active")||m.hasClass("active"))&&(Yr||Gr||Kr)&&ci(a,Ln),!r&&(Yr||Gr||Kr)&&ci(v,Ln))};0<qr&&!0!==t?k=setTimeout(e,qr):e()}}function Ke(n){var t={},r=ni(n),e=r.vn,i=Si.min(1,ee[r.j]/vr[r.j]);t[r.K]=Si.floor(100*i*1e6)/1e6+"%",dt()||r.ln.css(t),e.M=r.ln[0]["offset"+r.hn],e.D=i}function Je(n,t){var r,e,i=cn(t)==wi,o=Qt&&n,u=ni(n),f=u.vn,a="translate(",c=_i.v("transform"),s=_i.v("transition"),l=n?Zt[_e]():Zt[Oe](),v=t===di||i?l:t,h=f.M,d=u.sn[0]["offset"+u.hn],p=d-h,b={},m=(cr[we+u.hn]-cr["client"+u.hn])*(Ct.n&&o?-1:1),g=function(n){return isNaN(n/m)?0:Si.max(0,Si.min(1,n/m))},w=function(n){var t=p*n;return t=isNaN(t)?0:t,t=o&&!Ct.i?d-h-t:t,t=Si.max(0,t)},y=g(l),x=w(g(v)),_=w(y);f.N=m,f.L=l,f.R=y,ln?(r=o?-(d-h-x):x,e=n?a+r+"px, 0)":a+"0, "+r+"px)",b[c]=e,F&&(b[s]=i&&1<Si.abs(x-f.W)?function O(n){var t=_i.v("transition"),r=n.css(t);if(r)return r;for(var e,i,o,u="\\s*(([^,(]+(\\(.+?\\))?)+)[\\s,]*",f=new RegExp(u),a=new RegExp("^("+u+")+$"),c="property duration timing-function delay".split(" "),s=[],l=0,v=function(n){if(e=[],!n.match(a))return n;for(;n.match(f);)e.push(RegExp.$1),n=n.replace(f,me);return e};l<c[xi.l];l++)for(i=v(n.css(t+"-"+c[l])),o=0;o<i[xi.l];o++)s[o]=(s[o]?s[o]+xe:me)+i[o];return s.join(", ")}(u.ln)+", "+(c+xe+250)+"ms":me)):b[u.B]=x,dt()||(u.ln.css(b),ln&&F&&i&&u.ln.one(J,function(){Et||u.ln.css(s,me)})),f.W=x,f.P=_,f.F=d}function Ze(n,t){var r=t?"removeClass":"addClass",e=n?b:m,i=n?Tn:Hn;(n?s:l)[r](i),e[r](i)}function ni(n){return{K:n?de:pe,hn:n?"Width":"Height",B:n?le:ae,J:n?"Left":"Top",Q:n?pn:bn,Z:n?"X":"Y",j:n?"w":"h",dn:n?"l":"t",sn:n?s:b,ln:n?l:m,cn:n?a:v,vn:n?vn:hn}}function st(n){ir=ir||pt(Rn,!0),n?p&&Ht?si(ir.removeAttr(xi.s),Dn):gt(ir):p||Yt.append(ir)}function ti(n,t,r){if(!1!==r)if(Ht){var e,i=Vt.callbacks[n],o=n;"on"===o.substr(0,2)&&(o=o.substr(2,1).toLowerCase()+o.substr(3)),cn(i)==bi&&i.call(Ot,t),h(jn,function(){cn((e=this).on)==bi&&e.on(o,t)})}else Et||Fn.push({n:n,a:t})}function ri(n,t,r){r=r||[me,me,me,me],n[(t=t||me)+ae]=r[0],n[t+ce]=r[1],n[t+se]=r[2],n[t+le]=r[3]}function ei(n,t,r,e){return t=t||me,n=n||me,{t:e?0:ii(Yt.css(n+ae+t)),r:r?0:ii(Yt.css(n+ce+t)),b:e?0:ii(Yt.css(n+se+t)),l:r?0:ii(Yt.css(n+le+t))}}function lt(n,t){var r,e,i,o=function(n,t){if(i="",t&&typeof n==gi)for(e=n.split(xe),r=0;r<e[xi.l];r++)i+="|"+e[r]+"$";return i};return new RegExp("(^"+rn+"([-_].+|)$)"+o(Mr,n)+o(Dr,t),"g")}function vt(){var n=ar[xi.bCR]();return{x:ln&&1/(Si.round(n.width)/ar[xi.oW])||1,y:ln&&1/(Si.round(n.height)/ar[xi.oH])||1}}function ht(n){var t="ownerDocument",r="HTMLElement",e=n&&n[t]&&n[t].parentWindow||vi;return typeof e[r]==pi?n instanceof e[r]:n&&typeof n==pi&&null!==n&&1===n.nodeType&&typeof n.nodeName==gi}function ii(n,t){var r=t?parseFloat(n):parseInt(n,10);return isNaN(r)?0:r}function dt(){return Ir&&St.x&&St.y}function oi(){return Lt?er[0]:sr}function ui(r,n){return"<div "+(r?cn(r)==gi?'class="'+r+'"':function(){var n,t=me;if(Ci.isPlainObject(r))for(n in r)t+=("c"===n?"class":n)+'="'+r[n]+'" ';return t}():me)+">"+(n||me)+"</div>"}function pt(n,t){var r=cn(t)==wi,e=!r&&t||Yt;return p&&!e[xi.l]?null:p?e[r?"children":"find"](R+n.replace(/\s/g,R)).eq(0):Ci(ui(n))}function bt(n,t){for(var r,e=t.split(R),i=0;i<e.length;i++){if(!n[xi.hOP](e[i]))return;r=n[e[i]],i<e.length&&cn(r)==pi&&(n=r)}return r}function mt(n){var t=Vt.updateOnLoad;t=cn(t)==gi?t.split(xe):t,Oi.isA(t)&&!Et&&h(t,n)}function fi(n,t,r){if(r)return r;if(cn(n)!=pi||cn(t)!=pi)return n!==t;for(var e in n)if("c"!==e){if(!n[xi.hOP](e)||!t[xi.hOP](e))return!0;if(fi(n[e],t[e]))return!0}return!1}function ai(){return Ci.extend.apply(this,[!0].concat([].slice.call(arguments)))}function ci(n,t){return e.addClass.call(n,t)}function si(n,t){return e.removeClass.call(n,t)}function li(n,t,r){return(r?ci:si)(n,t)}function gt(n){return e.remove.call(n)}function wt(n,t){return e.find.call(n,t).eq(0)}}return zi&&zi.fn&&(zi.fn.overlayScrollbars=function(n,t){return zi.isPlainObject(n)?(zi.each(this,function(){q(this,n,t)}),this):q(this,n)}),q});
(function (global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory() :
  typeof define === 'function' && define.amd ? define(factory) :
  (global = global || self, global.GLightbox = factory());
}(this, (function () { 'use strict';

  function _classCallCheck(a, n) {
    if (!(a instanceof n)) throw new TypeError("Cannot call a class as a function");
  }
  function _defineProperties(e, r) {
    for (var t = 0; t < r.length; t++) {
      var o = r[t];
      o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, _toPropertyKey(o.key), o);
    }
  }
  function _createClass(e, r, t) {
    return r && _defineProperties(e.prototype, r), t && _defineProperties(e, t), Object.defineProperty(e, "prototype", {
      writable: !1
    }), e;
  }
  function _toPrimitive(t, r) {
    if ("object" != typeof t || !t) return t;
    var e = t[Symbol.toPrimitive];
    if (void 0 !== e) {
      var i = e.call(t, r || "default");
      if ("object" != typeof i) return i;
      throw new TypeError("@@toPrimitive must return a primitive value.");
    }
    return ("string" === r ? String : Number)(t);
  }
  function _toPropertyKey(t) {
    var i = _toPrimitive(t, "string");
    return "symbol" == typeof i ? i : i + "";
  }
  function _typeof(o) {
    "@babel/helpers - typeof";

    return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) {
      return typeof o;
    } : function (o) {
      return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o;
    }, _typeof(o);
  }

  var uid = Date.now();
  function extend() {
    var extended = {};
    var deep = true;
    var i = 0;
    var length = arguments.length;
    if (Object.prototype.toString.call(arguments[0]) === '[object Boolean]') {
      deep = arguments[0];
      i++;
    }
    var merge = function merge(obj) {
      for (var prop in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, prop)) {
          if (deep && Object.prototype.toString.call(obj[prop]) === '[object Object]') {
            extended[prop] = extend(true, extended[prop], obj[prop]);
          } else {
            extended[prop] = obj[prop];
          }
        }
      }
    };
    for (; i < length; i++) {
      var obj = arguments[i];
      merge(obj);
    }
    return extended;
  }
  function each(collection, callback) {
    if (isNode(collection) || collection === window || collection === document) {
      collection = [collection];
    }
    if (!isArrayLike(collection) && !isObject(collection)) {
      collection = [collection];
    }
    if (size(collection) == 0) {
      return;
    }
    if (isArrayLike(collection) && !isObject(collection)) {
      var l = collection.length,
        i = 0;
      for (; i < l; i++) {
        if (callback.call(collection[i], collection[i], i, collection) === false) {
          break;
        }
      }
    } else if (isObject(collection)) {
      for (var key in collection) {
        if (has(collection, key)) {
          if (callback.call(collection[key], collection[key], key, collection) === false) {
            break;
          }
        }
      }
    }
  }
  function getNodeEvents(node) {
    var name = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
    var fn = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
    var cache = node[uid] = node[uid] || [];
    var data = {
      all: cache,
      evt: null,
      found: null
    };
    if (name && fn && size(cache) > 0) {
      each(cache, function (cl, i) {
        if (cl.eventName == name && cl.fn.toString() == fn.toString()) {
          data.found = true;
          data.evt = i;
          return false;
        }
      });
    }
    return data;
  }
  function addEvent(eventName) {
    var _ref = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {},
      onElement = _ref.onElement,
      withCallback = _ref.withCallback,
      _ref$avoidDuplicate = _ref.avoidDuplicate,
      avoidDuplicate = _ref$avoidDuplicate === void 0 ? true : _ref$avoidDuplicate,
      _ref$once = _ref.once,
      once = _ref$once === void 0 ? false : _ref$once,
      _ref$useCapture = _ref.useCapture,
      useCapture = _ref$useCapture === void 0 ? false : _ref$useCapture;
    var thisArg = arguments.length > 2 ? arguments[2] : undefined;
    var element = onElement || [];
    if (isString(element)) {
      element = document.querySelectorAll(element);
    }
    function handler(event) {
      if (isFunction(withCallback)) {
        withCallback.call(thisArg, event, this);
      }
      if (once) {
        handler.destroy();
      }
    }
    handler.destroy = function () {
      each(element, function (el) {
        var events = getNodeEvents(el, eventName, handler);
        if (events.found) {
          events.all.splice(events.evt, 1);
        }
        if (el.removeEventListener) {
          el.removeEventListener(eventName, handler, useCapture);
        }
      });
    };
    each(element, function (el) {
      var events = getNodeEvents(el, eventName, handler);
      if (el.addEventListener && avoidDuplicate && !events.found || !avoidDuplicate) {
        el.addEventListener(eventName, handler, useCapture);
        events.all.push({
          eventName: eventName,
          fn: handler
        });
      }
    });
    return handler;
  }
  function addClass(node, name) {
    each(name.split(' '), function (cl) {
      return node.classList.add(cl);
    });
  }
  function removeClass(node, name) {
    each(name.split(' '), function (cl) {
      return node.classList.remove(cl);
    });
  }
  function hasClass(node, name) {
    return node.classList.contains(name);
  }
  function closest(elem, selector) {
    while (elem !== document.body) {
      elem = elem.parentElement;
      if (!elem) {
        return false;
      }
      var matches = typeof elem.matches == 'function' ? elem.matches(selector) : elem.msMatchesSelector(selector);
      if (matches) {
        return elem;
      }
    }
  }
  function animateElement(element) {
    var animation = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : '';
    var callback = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
    if (!element || animation === '') {
      return false;
    }
    if (animation === 'none') {
      if (isFunction(callback)) {
        callback();
      }
      return false;
    }
    var animationEnd = whichAnimationEvent();
    var animationNames = animation.split(' ');
    each(animationNames, function (name) {
      addClass(element, 'g' + name);
    });
    addEvent(animationEnd, {
      onElement: element,
      avoidDuplicate: false,
      once: true,
      withCallback: function withCallback(event, target) {
        each(animationNames, function (name) {
          removeClass(target, 'g' + name);
        });
        if (isFunction(callback)) {
          callback();
        }
      }
    });
  }
  function cssTransform(node) {
    var translate = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : '';
    if (translate === '') {
      node.style.webkitTransform = '';
      node.style.MozTransform = '';
      node.style.msTransform = '';
      node.style.OTransform = '';
      node.style.transform = '';
      return false;
    }
    node.style.webkitTransform = translate;
    node.style.MozTransform = translate;
    node.style.msTransform = translate;
    node.style.OTransform = translate;
    node.style.transform = translate;
  }
  function show(element) {
    element.style.display = 'block';
  }
  function hide(element) {
    element.style.display = 'none';
  }
  function createHTML(htmlStr) {
    var frag = document.createDocumentFragment(),
      temp = document.createElement('div');
    temp.innerHTML = htmlStr;
    while (temp.firstChild) {
      frag.appendChild(temp.firstChild);
    }
    return frag;
  }
  function windowSize() {
    return {
      width: window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth,
      height: window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight
    };
  }
  function whichAnimationEvent() {
    var t,
      el = document.createElement('fakeelement');
    var animations = {
      animation: 'animationend',
      OAnimation: 'oAnimationEnd',
      MozAnimation: 'animationend',
      WebkitAnimation: 'webkitAnimationEnd'
    };
    for (t in animations) {
      if (el.style[t] !== undefined) {
        return animations[t];
      }
    }
  }
  function whichTransitionEvent() {
    var t,
      el = document.createElement('fakeelement');
    var transitions = {
      transition: 'transitionend',
      OTransition: 'oTransitionEnd',
      MozTransition: 'transitionend',
      WebkitTransition: 'webkitTransitionEnd'
    };
    for (t in transitions) {
      if (el.style[t] !== undefined) {
        return transitions[t];
      }
    }
  }
  function createIframe(config) {
    var url = config.url,
      allow = config.allow,
      callback = config.callback,
      appendTo = config.appendTo;
    var iframe = document.createElement('iframe');
    iframe.className = 'vimeo-video gvideo';
    iframe.src = url;
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    if (allow) {
      iframe.setAttribute('allow', allow);
    }
    iframe.onload = function () {
      iframe.onload = null;
      addClass(iframe, 'node-ready');
      if (isFunction(callback)) {
        callback();
      }
    };
    if (appendTo) {
      appendTo.appendChild(iframe);
    }
    return iframe;
  }
  function waitUntil(check, onComplete, delay, timeout) {
    if (check()) {
      onComplete();
      return;
    }
    if (!delay) {
      delay = 100;
    }
    var timeoutPointer;
    var intervalPointer = setInterval(function () {
      if (!check()) {
        return;
      }
      clearInterval(intervalPointer);
      if (timeoutPointer) {
        clearTimeout(timeoutPointer);
      }
      onComplete();
    }, delay);
    if (timeout) {
      timeoutPointer = setTimeout(function () {
        clearInterval(intervalPointer);
      }, timeout);
    }
  }
  function injectAssets(url, waitFor, callback) {
    if (isNil(url)) {
      console.error('Inject assets error');
      return;
    }
    if (isFunction(waitFor)) {
      callback = waitFor;
      waitFor = false;
    }
    if (isString(waitFor) && waitFor in window) {
      if (isFunction(callback)) {
        callback();
      }
      return;
    }
    var found;
    if (url.indexOf('.css') !== -1) {
      found = document.querySelectorAll('link[href="' + url + '"]');
      if (found && found.length > 0) {
        if (isFunction(callback)) {
          callback();
        }
        return;
      }
      var head = document.getElementsByTagName('head')[0];
      var headStyles = head.querySelectorAll('link[rel="stylesheet"]');
      var link = document.createElement('link');
      link.rel = 'stylesheet';
      link.type = 'text/css';
      link.href = url;
      link.media = 'all';
      if (headStyles) {
        head.insertBefore(link, headStyles[0]);
      } else {
        head.appendChild(link);
      }
      if (isFunction(callback)) {
        callback();
      }
      return;
    }
    found = document.querySelectorAll('script[src="' + url + '"]');
    if (found && found.length > 0) {
      if (isFunction(callback)) {
        if (isString(waitFor)) {
          waitUntil(function () {
            return typeof window[waitFor] !== 'undefined';
          }, function () {
            callback();
          });
          return false;
        }
        callback();
      }
      return;
    }
    var script = document.createElement('script');
    script.type = 'text/javascript';
    script.src = url;
    script.onload = function () {
      if (isFunction(callback)) {
        if (isString(waitFor)) {
          waitUntil(function () {
            return typeof window[waitFor] !== 'undefined';
          }, function () {
            callback();
          });
          return false;
        }
        callback();
      }
    };
    document.body.appendChild(script);
  }
  function isMobile() {
    return 'navigator' in window && window.navigator.userAgent.match(/(iPad)|(iPhone)|(iPod)|(Android)|(PlayBook)|(BB10)|(BlackBerry)|(Opera Mini)|(IEMobile)|(webOS)|(MeeGo)/i);
  }
  function isTouch() {
    return isMobile() !== null || document.createTouch !== undefined || 'ontouchstart' in window || 'onmsgesturechange' in window || navigator.msMaxTouchPoints;
  }
  function isFunction(f) {
    return typeof f === 'function';
  }
  function isString(s) {
    return typeof s === 'string';
  }
  function isNode(el) {
    return !!(el && el.nodeType && el.nodeType == 1);
  }
  function isArray(ar) {
    return Array.isArray(ar);
  }
  function isArrayLike(ar) {
    return ar && ar.length && isFinite(ar.length);
  }
  function isObject(o) {
    var type = _typeof(o);
    return type === 'object' && o != null && !isFunction(o) && !isArray(o);
  }
  function isNil(o) {
    return o == null;
  }
  function has(obj, key) {
    return obj !== null && hasOwnProperty.call(obj, key);
  }
  function size(o) {
    if (isObject(o)) {
      if (o.keys) {
        return o.keys().length;
      }
      var l = 0;
      for (var k in o) {
        if (has(o, k)) {
          l++;
        }
      }
      return l;
    } else {
      return o.length;
    }
  }
  function isNumber(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
  }

  function getNextFocusElement() {
    var current = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : -1;
    var btns = document.querySelectorAll('.gbtn[data-taborder]:not(.disabled)');
    if (!btns.length) {
      return false;
    }
    if (btns.length == 1) {
      return btns[0];
    }
    if (typeof current == 'string') {
      current = parseInt(current);
    }
    var orders = [];
    each(btns, function (btn) {
      orders.push(btn.getAttribute('data-taborder'));
    });
    var highestOrder = Math.max.apply(Math, orders.map(function (order) {
      return parseInt(order);
    }));
    var newIndex = current < 0 ? 1 : current + 1;
    if (newIndex > highestOrder) {
      newIndex = '1';
    }
    var nextOrders = orders.filter(function (el) {
      return el >= parseInt(newIndex);
    });
    var nextFocus = nextOrders.sort()[0];
    return document.querySelector(".gbtn[data-taborder=\"".concat(nextFocus, "\"]"));
  }
  function keyboardNavigation(instance) {
    if (instance.events.hasOwnProperty('keyboard')) {
      return false;
    }
    instance.events['keyboard'] = addEvent('keydown', {
      onElement: window,
      withCallback: function withCallback(event, target) {
        event = event || window.event;
        var key = event.keyCode;
        if (key == 9) {
          var focusedButton = document.querySelector('.gbtn.focused');
          if (!focusedButton) {
            var activeElement = document.activeElement && document.activeElement.nodeName ? document.activeElement.nodeName.toLocaleLowerCase() : false;
            if (activeElement == 'input' || activeElement == 'textarea' || activeElement == 'button') {
              return;
            }
          }
          event.preventDefault();
          var btns = document.querySelectorAll('.gbtn[data-taborder]');
          if (!btns || btns.length <= 0) {
            return;
          }
          if (!focusedButton) {
            var first = getNextFocusElement();
            if (first) {
              first.focus();
              addClass(first, 'focused');
            }
            return;
          }
          var currentFocusOrder = focusedButton.getAttribute('data-taborder');
          var nextFocus = getNextFocusElement(currentFocusOrder);
          removeClass(focusedButton, 'focused');
          if (nextFocus) {
            nextFocus.focus();
            addClass(nextFocus, 'focused');
          }
        }
        if (key == 39) {
          instance.nextSlide();
        }
        if (key == 37) {
          instance.prevSlide();
        }
        if (key == 27) {
          instance.close();
        }
      }
    });
  }

  var ZoomImages = function () {
    function ZoomImages(el, slide) {
      var _this = this;
      var onclose = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
      _classCallCheck(this, ZoomImages);
      this.img = el;
      this.slide = slide;
      this.onclose = onclose;
      if (this.img.setZoomEvents) {
        return false;
      }
      this.active = false;
      this.zoomedIn = false;
      this.dragging = false;
      this.currentX = null;
      this.currentY = null;
      this.initialX = null;
      this.initialY = null;
      this.xOffset = 0;
      this.yOffset = 0;
      this.img.addEventListener('mousedown', function (e) {
        return _this.dragStart(e);
      }, false);
      this.img.addEventListener('mouseup', function (e) {
        return _this.dragEnd(e);
      }, false);
      this.img.addEventListener('mousemove', function (e) {
        return _this.drag(e);
      }, false);
      this.img.addEventListener('click', function (e) {
        if (_this.slide.classList.contains('dragging-nav')) {
          _this.zoomOut();
          return false;
        }
        if (!_this.zoomedIn) {
          return _this.zoomIn();
        }
        if (_this.zoomedIn && !_this.dragging) {
          _this.zoomOut();
        }
      }, false);
      this.img.setZoomEvents = true;
    }
    return _createClass(ZoomImages, [{
      key: "zoomIn",
      value: function zoomIn() {
        var winWidth = this.widowWidth();
        if (this.zoomedIn || winWidth <= 768) {
          return;
        }
        var img = this.img;
        img.setAttribute('data-style', img.getAttribute('style'));
        img.style.maxWidth = img.naturalWidth + 'px';
        img.style.maxHeight = img.naturalHeight + 'px';
        if (img.naturalWidth > winWidth) {
          var centerX = winWidth / 2 - img.naturalWidth / 2;
          this.setTranslate(this.img.parentNode, centerX, 0);
        }
        this.slide.classList.add('zoomed');
        this.zoomedIn = true;
      }
    }, {
      key: "zoomOut",
      value: function zoomOut() {
        this.img.parentNode.setAttribute('style', '');
        this.img.setAttribute('style', this.img.getAttribute('data-style'));
        this.slide.classList.remove('zoomed');
        this.zoomedIn = false;
        this.currentX = null;
        this.currentY = null;
        this.initialX = null;
        this.initialY = null;
        this.xOffset = 0;
        this.yOffset = 0;
        if (this.onclose && typeof this.onclose == 'function') {
          this.onclose();
        }
      }
    }, {
      key: "dragStart",
      value: function dragStart(e) {
        e.preventDefault();
        if (!this.zoomedIn) {
          this.active = false;
          return;
        }
        if (e.type === 'touchstart') {
          this.initialX = e.touches[0].clientX - this.xOffset;
          this.initialY = e.touches[0].clientY - this.yOffset;
        } else {
          this.initialX = e.clientX - this.xOffset;
          this.initialY = e.clientY - this.yOffset;
        }
        if (e.target === this.img) {
          this.active = true;
          this.img.classList.add('dragging');
        }
      }
    }, {
      key: "dragEnd",
      value: function dragEnd(e) {
        var _this2 = this;
        e.preventDefault();
        this.initialX = this.currentX;
        this.initialY = this.currentY;
        this.active = false;
        setTimeout(function () {
          _this2.dragging = false;
          _this2.img.isDragging = false;
          _this2.img.classList.remove('dragging');
        }, 100);
      }
    }, {
      key: "drag",
      value: function drag(e) {
        if (this.active) {
          e.preventDefault();
          if (e.type === 'touchmove') {
            this.currentX = e.touches[0].clientX - this.initialX;
            this.currentY = e.touches[0].clientY - this.initialY;
          } else {
            this.currentX = e.clientX - this.initialX;
            this.currentY = e.clientY - this.initialY;
          }
          this.xOffset = this.currentX;
          this.yOffset = this.currentY;
          this.img.isDragging = true;
          this.dragging = true;
          this.setTranslate(this.img, this.currentX, this.currentY);
        }
      }
    }, {
      key: "onMove",
      value: function onMove(e) {
        if (!this.zoomedIn) {
          return;
        }
        var xOffset = e.clientX - this.img.naturalWidth / 2;
        var yOffset = e.clientY - this.img.naturalHeight / 2;
        this.setTranslate(this.img, xOffset, yOffset);
      }
    }, {
      key: "setTranslate",
      value: function setTranslate(node, xPos, yPos) {
        node.style.transform = 'translate3d(' + xPos + 'px, ' + yPos + 'px, 0)';
      }
    }, {
      key: "widowWidth",
      value: function widowWidth() {
        return window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
      }
    }]);
  }();

  var DragSlides = function () {
    function DragSlides() {
      var _this = this;
      var config = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      _classCallCheck(this, DragSlides);
      var dragEl = config.dragEl,
        _config$toleranceX = config.toleranceX,
        toleranceX = _config$toleranceX === void 0 ? 40 : _config$toleranceX,
        _config$toleranceY = config.toleranceY,
        toleranceY = _config$toleranceY === void 0 ? 65 : _config$toleranceY,
        _config$slide = config.slide,
        slide = _config$slide === void 0 ? null : _config$slide,
        _config$instance = config.instance,
        instance = _config$instance === void 0 ? null : _config$instance;
      this.el = dragEl;
      this.active = false;
      this.dragging = false;
      this.currentX = null;
      this.currentY = null;
      this.initialX = null;
      this.initialY = null;
      this.xOffset = 0;
      this.yOffset = 0;
      this.direction = null;
      this.lastDirection = null;
      this.toleranceX = toleranceX;
      this.toleranceY = toleranceY;
      this.toleranceReached = false;
      this.dragContainer = this.el;
      this.slide = slide;
      this.instance = instance;
      this.el.addEventListener('mousedown', function (e) {
        return _this.dragStart(e);
      }, false);
      this.el.addEventListener('mouseup', function (e) {
        return _this.dragEnd(e);
      }, false);
      this.el.addEventListener('mousemove', function (e) {
        return _this.drag(e);
      }, false);
    }
    return _createClass(DragSlides, [{
      key: "dragStart",
      value: function dragStart(e) {
        if (this.slide.classList.contains('zoomed')) {
          this.active = false;
          return;
        }
        if (e.type === 'touchstart') {
          this.initialX = e.touches[0].clientX - this.xOffset;
          this.initialY = e.touches[0].clientY - this.yOffset;
        } else {
          this.initialX = e.clientX - this.xOffset;
          this.initialY = e.clientY - this.yOffset;
        }
        var clicked = e.target.nodeName.toLowerCase();
        var exludeClicks = ['input', 'select', 'textarea', 'button', 'a'];
        if (e.target.classList.contains('nodrag') || closest(e.target, '.nodrag') || exludeClicks.indexOf(clicked) !== -1) {
          this.active = false;
          return;
        }
        e.preventDefault();
        if (e.target === this.el || clicked !== 'img' && closest(e.target, '.gslide-inline')) {
          this.active = true;
          this.el.classList.add('dragging');
          this.dragContainer = closest(e.target, '.ginner-container');
        }
      }
    }, {
      key: "dragEnd",
      value: function dragEnd(e) {
        var _this2 = this;
        e && e.preventDefault();
        this.initialX = 0;
        this.initialY = 0;
        this.currentX = null;
        this.currentY = null;
        this.initialX = null;
        this.initialY = null;
        this.xOffset = 0;
        this.yOffset = 0;
        this.active = false;
        if (this.doSlideChange) {
          this.instance.preventOutsideClick = true;
          this.doSlideChange == 'right' && this.instance.prevSlide();
          this.doSlideChange == 'left' && this.instance.nextSlide();
        }
        if (this.doSlideClose) {
          this.instance.close();
        }
        if (!this.toleranceReached) {
          this.setTranslate(this.dragContainer, 0, 0, true);
        }
        setTimeout(function () {
          _this2.instance.preventOutsideClick = false;
          _this2.toleranceReached = false;
          _this2.lastDirection = null;
          _this2.dragging = false;
          _this2.el.isDragging = false;
          _this2.el.classList.remove('dragging');
          _this2.slide.classList.remove('dragging-nav');
          _this2.dragContainer.style.transform = '';
          _this2.dragContainer.style.transition = '';
        }, 100);
      }
    }, {
      key: "drag",
      value: function drag(e) {
        if (this.active) {
          e.preventDefault();
          this.slide.classList.add('dragging-nav');
          if (e.type === 'touchmove') {
            this.currentX = e.touches[0].clientX - this.initialX;
            this.currentY = e.touches[0].clientY - this.initialY;
          } else {
            this.currentX = e.clientX - this.initialX;
            this.currentY = e.clientY - this.initialY;
          }
          this.xOffset = this.currentX;
          this.yOffset = this.currentY;
          this.el.isDragging = true;
          this.dragging = true;
          this.doSlideChange = false;
          this.doSlideClose = false;
          var currentXInt = Math.abs(this.currentX);
          var currentYInt = Math.abs(this.currentY);
          if (currentXInt > 0 && currentXInt >= Math.abs(this.currentY) && (!this.lastDirection || this.lastDirection == 'x')) {
            this.yOffset = 0;
            this.lastDirection = 'x';
            this.setTranslate(this.dragContainer, this.currentX, 0);
            var doChange = this.shouldChange();
            if (!this.instance.settings.dragAutoSnap && doChange) {
              this.doSlideChange = doChange;
            }
            if (this.instance.settings.dragAutoSnap && doChange) {
              this.instance.preventOutsideClick = true;
              this.toleranceReached = true;
              this.active = false;
              this.instance.preventOutsideClick = true;
              this.dragEnd(null);
              doChange == 'right' && this.instance.prevSlide();
              doChange == 'left' && this.instance.nextSlide();
              return;
            }
          }
          if (this.toleranceY > 0 && currentYInt > 0 && currentYInt >= currentXInt && (!this.lastDirection || this.lastDirection == 'y')) {
            this.xOffset = 0;
            this.lastDirection = 'y';
            this.setTranslate(this.dragContainer, 0, this.currentY);
            var doClose = this.shouldClose();
            if (!this.instance.settings.dragAutoSnap && doClose) {
              this.doSlideClose = true;
            }
            if (this.instance.settings.dragAutoSnap && doClose) {
              this.instance.close();
            }
            return;
          }
        }
      }
    }, {
      key: "shouldChange",
      value: function shouldChange() {
        var doChange = false;
        var currentXInt = Math.abs(this.currentX);
        if (currentXInt >= this.toleranceX) {
          var dragDir = this.currentX > 0 ? 'right' : 'left';
          if (dragDir == 'left' && this.slide !== this.slide.parentNode.lastChild || dragDir == 'right' && this.slide !== this.slide.parentNode.firstChild) {
            doChange = dragDir;
          }
        }
        return doChange;
      }
    }, {
      key: "shouldClose",
      value: function shouldClose() {
        var doClose = false;
        var currentYInt = Math.abs(this.currentY);
        if (currentYInt >= this.toleranceY) {
          doClose = true;
        }
        return doClose;
      }
    }, {
      key: "setTranslate",
      value: function setTranslate(node, xPos, yPos) {
        var animated = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : false;
        if (animated) {
          node.style.transition = 'all .2s ease';
        } else {
          node.style.transition = '';
        }
        node.style.transform = "translate3d(".concat(xPos, "px, ").concat(yPos, "px, 0)");
      }
    }]);
  }();

  function slideImage(slide, data, index, callback) {
    var slideMedia = slide.querySelector('.gslide-media');
    var img = new Image();
    var titleID = 'gSlideTitle_' + index;
    var textID = 'gSlideDesc_' + index;
    img.addEventListener('load', function () {
      if (isFunction(callback)) {
        callback();
      }
    }, false);
    img.src = data.href;
    if (data.sizes != '' && data.srcset != '') {
      img.sizes = data.sizes;
      img.srcset = data.srcset;
    }
    img.alt = '';
    if (!isNil(data.alt) && data.alt !== '') {
      img.alt = data.alt;
    }
    if (data.title !== '') {
      img.setAttribute('aria-labelledby', titleID);
    }
    if (data.description !== '') {
      img.setAttribute('aria-describedby', textID);
    }
    if (data.hasOwnProperty('_hasCustomWidth') && data._hasCustomWidth) {
      img.style.width = data.width;
    }
    if (data.hasOwnProperty('_hasCustomHeight') && data._hasCustomHeight) {
      img.style.height = data.height;
    }
    slideMedia.insertBefore(img, slideMedia.firstChild);
    return;
  }

  function slideVideo(slide, data, index, callback) {
    var _this = this;
    var slideContainer = slide.querySelector('.ginner-container');
    var videoID = 'gvideo' + index;
    var slideMedia = slide.querySelector('.gslide-media');
    var videoPlayers = this.getAllPlayers();
    addClass(slideContainer, 'gvideo-container');
    slideMedia.insertBefore(createHTML('<div class="gvideo-wrapper"></div>'), slideMedia.firstChild);
    var videoWrapper = slide.querySelector('.gvideo-wrapper');
    injectAssets(this.settings.plyr.css, 'Plyr');
    var url = data.href;
    var provider = data === null || data === void 0 ? void 0 : data.videoProvider;
    var customPlaceholder = false;
    slideMedia.style.maxWidth = data.width;
    injectAssets(this.settings.plyr.js, 'Plyr', function () {
      if (!provider && url.match(/vimeo\.com\/([0-9]*)/)) {
        provider = 'vimeo';
      }
      if (!provider && (url.match(/(youtube\.com|youtube-nocookie\.com)\/watch\?v=([a-zA-Z0-9\-_]+)/) || url.match(/youtu\.be\/([a-zA-Z0-9\-_]+)/) || url.match(/(youtube\.com|youtube-nocookie\.com)\/embed\/([a-zA-Z0-9\-_]+)/) || url.match(/(youtube\.com|youtube-nocookie\.com)\/shorts\/([a-zA-Z0-9\-_]+)/))) {
        provider = 'youtube';
      }
      if (provider === 'local' || !provider) {
        provider = 'local';
        var html = '<video id="' + videoID + '" ';
        html += "style=\"background:#000; max-width: ".concat(data.width, ";\" ");
        html += 'preload="metadata" ';
        html += 'x-webkit-airplay="allow" ';
        html += 'playsinline ';
        html += 'controls ';
        html += 'class="gvideo-local">';
        html += "<source src=\"".concat(url, "\">");
        html += '</video>';
        customPlaceholder = createHTML(html);
      }
      var placeholder = customPlaceholder ? customPlaceholder : createHTML("<div id=\"".concat(videoID, "\" data-plyr-provider=\"").concat(provider, "\" data-plyr-embed-id=\"").concat(url, "\"></div>"));
      addClass(videoWrapper, "".concat(provider, "-video gvideo"));
      videoWrapper.appendChild(placeholder);
      videoWrapper.setAttribute('data-id', videoID);
      videoWrapper.setAttribute('data-index', index);
      var playerConfig = has(_this.settings.plyr, 'config') ? _this.settings.plyr.config : {};
      var player = new Plyr('#' + videoID, playerConfig);
      player.on('ready', function (event) {
        videoPlayers[videoID] = event.detail.plyr;
        if (isFunction(callback)) {
          callback();
        }
      });
      waitUntil(function () {
        return slide.querySelector('iframe') && slide.querySelector('iframe').dataset.ready == 'true';
      }, function () {
        _this.resize(slide);
      });
      player.on('enterfullscreen', handleMediaFullScreen);
      player.on('exitfullscreen', handleMediaFullScreen);
    });
  }
  function handleMediaFullScreen(event) {
    var media = closest(event.target, '.gslide-media');
    if (event.type === 'enterfullscreen') {
      addClass(media, 'fullscreen');
    }
    if (event.type === 'exitfullscreen') {
      removeClass(media, 'fullscreen');
    }
  }

  function slideInline(slide, data, index, callback) {
    var _this = this;
    var slideMedia = slide.querySelector('.gslide-media');
    var hash = has(data, 'href') && data.href ? data.href.split('#').pop().trim() : false;
    var content = has(data, 'content') && data.content ? data.content : false;
    var innerContent;
    if (content) {
      if (isString(content)) {
        innerContent = createHTML("<div class=\"ginlined-content\">".concat(content, "</div>"));
      }
      if (isNode(content)) {
        if (content.style.display == 'none') {
          content.style.display = 'block';
        }
        var container = document.createElement('div');
        container.className = 'ginlined-content';
        container.appendChild(content);
        innerContent = container;
      }
    }
    if (hash) {
      var div = document.getElementById(hash);
      if (!div) {
        return false;
      }
      var cloned = div.cloneNode(true);
      cloned.style.height = data.height;
      cloned.style.maxWidth = data.width;
      addClass(cloned, 'ginlined-content');
      innerContent = cloned;
    }
    if (!innerContent) {
      console.error('Unable to append inline slide content', data);
      return false;
    }
    slideMedia.style.height = data.height;
    slideMedia.style.width = data.width;
    slideMedia.appendChild(innerContent);
    this.events['inlineclose' + hash] = addEvent('click', {
      onElement: slideMedia.querySelectorAll('.gtrigger-close'),
      withCallback: function withCallback(e) {
        e.preventDefault();
        _this.close();
      }
    });
    if (isFunction(callback)) {
      callback();
    }
    return;
  }

  function slideIframe(slide, data, index, callback) {
    var slideMedia = slide.querySelector('.gslide-media');
    var iframe = createIframe({
      url: data.href,
      callback: callback
    });
    slideMedia.parentNode.style.maxWidth = data.width;
    slideMedia.parentNode.style.height = data.height;
    slideMedia.appendChild(iframe);
    return;
  }

  var SlideConfigParser = function () {
    function SlideConfigParser() {
      var slideParamas = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      _classCallCheck(this, SlideConfigParser);
      this.defaults = {
        href: '',
        sizes: '',
        srcset: '',
        title: '',
        type: '',
        videoProvider: '',
        description: '',
        alt: '',
        descPosition: 'bottom',
        effect: '',
        width: '',
        height: '',
        content: false,
        zoomable: true,
        draggable: true
      };
      if (isObject(slideParamas)) {
        this.defaults = extend(this.defaults, slideParamas);
      }
    }
    return _createClass(SlideConfigParser, [{
      key: "sourceType",
      value: function sourceType(url) {
        var origin = url;
        url = url.toLowerCase();
        if (url.match(/\.(jpeg|jpg|jpe|gif|png|apn|webp|avif|svg)/) !== null) {
          return 'image';
        }
        if (url.match(/(youtube\.com|youtube-nocookie\.com)\/watch\?v=([a-zA-Z0-9\-_]+)/) || url.match(/youtu\.be\/([a-zA-Z0-9\-_]+)/) || url.match(/(youtube\.com|youtube-nocookie\.com)\/embed\/([a-zA-Z0-9\-_]+)/) || url.match(/(youtube\.com|youtube-nocookie\.com)\/shorts\/([a-zA-Z0-9\-_]+)/)) {
          return 'video';
        }
        if (url.match(/vimeo\.com\/([0-9]*)/)) {
          return 'video';
        }
        if (url.match(/\.(mp4|ogg|webm|mov)/) !== null) {
          return 'video';
        }
        if (url.match(/\.(mp3|wav|wma|aac|ogg)/) !== null) {
          return 'audio';
        }
        if (url.indexOf('#') > -1) {
          var hash = origin.split('#').pop();
          if (hash.trim() !== '') {
            return 'inline';
          }
        }
        if (url.indexOf('goajax=true') > -1) {
          return 'ajax';
        }
        return 'external';
      }
    }, {
      key: "parseConfig",
      value: function parseConfig(element, settings) {
        var _this = this;
        var data = extend({
          descPosition: settings.descPosition
        }, this.defaults);
        if (isObject(element) && !isNode(element)) {
          if (!has(element, 'type')) {
            if (has(element, 'content') && element.content) {
              element.type = 'inline';
            } else if (has(element, 'href')) {
              element.type = this.sourceType(element.href);
            }
          }
          var objectData = extend(data, element);
          this.setSize(objectData, settings);
          return objectData;
        }
        var url = '';
        var config = element.getAttribute('data-glightbox');
        var nodeType = element.nodeName.toLowerCase();
        if (nodeType === 'a') {
          url = element.href;
        }
        if (nodeType === 'img') {
          url = element.src;
          data.alt = element.alt;
        }
        data.href = url;
        each(data, function (val, key) {
          if (has(settings, key) && key !== 'width') {
            data[key] = settings[key];
          }
          var nodeData = element.dataset[key];
          if (!isNil(nodeData)) {
            data[key] = _this.sanitizeValue(nodeData);
          }
        });
        if (data.content) {
          data.type = 'inline';
        }
        if (!data.type && url) {
          data.type = this.sourceType(url);
        }
        if (!isNil(config)) {
          var cleanKeys = [];
          each(data, function (v, k) {
            cleanKeys.push(';\\s?' + k);
          });
          cleanKeys = cleanKeys.join('\\s?:|');
          if (config.trim() !== '') {
            each(data, function (val, key) {
              var str = config;
              var match = 's?' + key + 's?:s?(.*?)(' + cleanKeys + 's?:|$)';
              var regex = new RegExp(match);
              var matches = str.match(regex);
              if (matches && matches.length && matches[1]) {
                var value = matches[1].trim().replace(/;\s*$/, '');
                data[key] = _this.sanitizeValue(value);
              }
            });
          }
        } else {
          if (!data.title && nodeType == 'a') {
            var title = element.title;
            if (!isNil(title) && title !== '') {
              data.title = title;
            }
          }
          if (!data.title && nodeType == 'img') {
            var alt = element.alt;
            if (!isNil(alt) && alt !== '') {
              data.title = alt;
            }
          }
        }
        if (data.description && data.description.substring(0, 1) === '.') {
          var description;
          try {
            description = document.querySelector(data.description).innerHTML;
          } catch (error) {
            if (!(error instanceof DOMException)) {
              throw error;
            }
          }
          if (description) {
            data.description = description;
          }
        }
        if (!data.description) {
          var nodeDesc = element.querySelector('.glightbox-desc');
          if (nodeDesc) {
            data.description = nodeDesc.innerHTML;
          }
        }
        this.setSize(data, settings, element);
        this.slideConfig = data;
        return data;
      }
    }, {
      key: "setSize",
      value: function setSize(data, settings) {
        var element = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : null;
        var defaultWith = data.type == 'video' ? this.checkSize(settings.videosWidth) : this.checkSize(settings.width);
        var defaultHeight = this.checkSize(settings.height);
        data.width = has(data, 'width') && data.width !== '' ? this.checkSize(data.width) : defaultWith;
        data.height = has(data, 'height') && data.height !== '' ? this.checkSize(data.height) : defaultHeight;
        if (element && data.type == 'image') {
          data._hasCustomWidth = element.dataset.width ? true : false;
          data._hasCustomHeight = element.dataset.height ? true : false;
        }
        return data;
      }
    }, {
      key: "checkSize",
      value: function checkSize(size) {
        return isNumber(size) ? "".concat(size, "px") : size;
      }
    }, {
      key: "sanitizeValue",
      value: function sanitizeValue(val) {
        if (val !== 'true' && val !== 'false') {
          return val;
        }
        return val === 'true';
      }
    }]);
  }();

  var Slide = function () {
    function Slide(el, instance, index) {
      _classCallCheck(this, Slide);
      this.element = el;
      this.instance = instance;
      this.index = index;
    }
    return _createClass(Slide, [{
      key: "setContent",
      value: function setContent() {
        var _this = this;
        var slide = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
        var callback = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
        if (hasClass(slide, 'loaded')) {
          return false;
        }
        var settings = this.instance.settings;
        var slideConfig = this.slideConfig;
        var isMobileDevice = isMobile();
        if (isFunction(settings.beforeSlideLoad)) {
          settings.beforeSlideLoad({
            index: this.index,
            slide: slide,
            player: false
          });
        }
        var type = slideConfig.type;
        var position = slideConfig.descPosition;
        var slideMedia = slide.querySelector('.gslide-media');
        var slideTitle = slide.querySelector('.gslide-title');
        var slideText = slide.querySelector('.gslide-desc');
        var slideDesc = slide.querySelector('.gdesc-inner');
        var finalCallback = callback;
        var titleID = 'gSlideTitle_' + this.index;
        var textID = 'gSlideDesc_' + this.index;
        if (isFunction(settings.afterSlideLoad)) {
          finalCallback = function finalCallback() {
            if (isFunction(callback)) {
              callback();
            }
            settings.afterSlideLoad({
              index: _this.index,
              slide: slide,
              player: _this.instance.getSlidePlayerInstance(_this.index)
            });
          };
        }
        if (slideConfig.title == '' && slideConfig.description == '') {
          if (slideDesc) {
            slideDesc.parentNode.parentNode.removeChild(slideDesc.parentNode);
          }
        } else {
          if (slideTitle && slideConfig.title !== '') {
            slideTitle.id = titleID;
            slideTitle.innerHTML = slideConfig.title;
          } else {
            slideTitle.parentNode.removeChild(slideTitle);
          }
          if (slideText && slideConfig.description !== '') {
            slideText.id = textID;
            if (isMobileDevice && settings.moreLength > 0) {
              slideConfig.smallDescription = this.slideShortDesc(slideConfig.description, settings.moreLength, settings.moreText);
              slideText.innerHTML = slideConfig.smallDescription;
              this.descriptionEvents(slideText, slideConfig);
            } else {
              slideText.innerHTML = slideConfig.description;
            }
          } else {
            slideText.parentNode.removeChild(slideText);
          }
          addClass(slideMedia.parentNode, "desc-".concat(position));
          addClass(slideDesc.parentNode, "description-".concat(position));
        }
        addClass(slideMedia, "gslide-".concat(type));
        addClass(slide, 'loaded');
        if (type === 'video') {
          slideVideo.apply(this.instance, [slide, slideConfig, this.index, finalCallback]);
          return;
        }
        if (type === 'external') {
          slideIframe.apply(this, [slide, slideConfig, this.index, finalCallback]);
          return;
        }
        if (type === 'inline') {
          slideInline.apply(this.instance, [slide, slideConfig, this.index, finalCallback]);
          if (slideConfig.draggable) {
            new DragSlides({
              dragEl: slide.querySelector('.gslide-inline'),
              toleranceX: settings.dragToleranceX,
              toleranceY: settings.dragToleranceY,
              slide: slide,
              instance: this.instance
            });
          }
          return;
        }
        if (type === 'image') {
          slideImage(slide, slideConfig, this.index, function () {
            var img = slide.querySelector('img');
            if (slideConfig.draggable) {
              new DragSlides({
                dragEl: img,
                toleranceX: settings.dragToleranceX,
                toleranceY: settings.dragToleranceY,
                slide: slide,
                instance: _this.instance
              });
            }
            if (slideConfig.zoomable && img.naturalWidth > img.offsetWidth) {
              addClass(img, 'zoomable');
              new ZoomImages(img, slide, function () {
                _this.instance.resize();
              });
            }
            if (isFunction(finalCallback)) {
              finalCallback();
            }
          });
          return;
        }
        if (isFunction(finalCallback)) {
          finalCallback();
        }
      }
    }, {
      key: "slideShortDesc",
      value: function slideShortDesc(string) {
        var n = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 50;
        var wordBoundary = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
        var div = document.createElement('div');
        div.innerHTML = string;
        var cleanedString = div.innerText;
        var useWordBoundary = wordBoundary;
        string = cleanedString.trim();
        if (string.length <= n) {
          return string;
        }
        var subString = string.substr(0, n - 1);
        if (!useWordBoundary) {
          return subString;
        }
        div = null;
        return subString + '... <a href="#" class="desc-more">' + wordBoundary + '</a>';
      }
    }, {
      key: "descriptionEvents",
      value: function descriptionEvents(desc, data) {
        var _this2 = this;
        var moreLink = desc.querySelector('.desc-more');
        if (!moreLink) {
          return false;
        }
        addEvent('click', {
          onElement: moreLink,
          withCallback: function withCallback(event, target) {
            event.preventDefault();
            var body = document.body;
            var desc = closest(target, '.gslide-desc');
            if (!desc) {
              return false;
            }
            desc.innerHTML = data.description;
            addClass(body, 'gdesc-open');
            var shortEvent = addEvent('click', {
              onElement: [body, closest(desc, '.gslide-description')],
              withCallback: function withCallback(event, target) {
                if (event.target.nodeName.toLowerCase() !== 'a') {
                  removeClass(body, 'gdesc-open');
                  addClass(body, 'gdesc-closed');
                  desc.innerHTML = data.smallDescription;
                  _this2.descriptionEvents(desc, data);
                  setTimeout(function () {
                    removeClass(body, 'gdesc-closed');
                  }, 400);
                  shortEvent.destroy();
                }
              }
            });
          }
        });
      }
    }, {
      key: "create",
      value: function create() {
        return createHTML(this.instance.settings.slideHTML);
      }
    }, {
      key: "getConfig",
      value: function getConfig() {
        if (!isNode(this.element) && !this.element.hasOwnProperty('draggable')) {
          this.element.draggable = this.instance.settings.draggable;
        }
        var parser = new SlideConfigParser(this.instance.settings.slideExtraAttributes);
        this.slideConfig = parser.parseConfig(this.element, this.instance.settings);
        return this.slideConfig;
      }
    }]);
  }();

  function getLen(v) {
    return Math.sqrt(v.x * v.x + v.y * v.y);
  }
  function dot(v1, v2) {
    return v1.x * v2.x + v1.y * v2.y;
  }
  function getAngle(v1, v2) {
    var mr = getLen(v1) * getLen(v2);
    if (mr === 0) {
      return 0;
    }
    var r = dot(v1, v2) / mr;
    if (r > 1) {
      r = 1;
    }
    return Math.acos(r);
  }
  function cross(v1, v2) {
    return v1.x * v2.y - v2.x * v1.y;
  }
  function getRotateAngle(v1, v2) {
    var angle = getAngle(v1, v2);
    if (cross(v1, v2) > 0) {
      angle *= -1;
    }
    return angle * 180 / Math.PI;
  }
  var EventsHandlerAdmin = function () {
    function EventsHandlerAdmin(el) {
      _classCallCheck(this, EventsHandlerAdmin);
      this.handlers = [];
      this.el = el;
    }
    return _createClass(EventsHandlerAdmin, [{
      key: "add",
      value: function add(handler) {
        this.handlers.push(handler);
      }
    }, {
      key: "del",
      value: function del(handler) {
        if (!handler) {
          this.handlers = [];
        }
        for (var i = this.handlers.length; i >= 0; i--) {
          if (this.handlers[i] === handler) {
            this.handlers.splice(i, 1);
          }
        }
      }
    }, {
      key: "dispatch",
      value: function dispatch() {
        for (var i = 0, len = this.handlers.length; i < len; i++) {
          var handler = this.handlers[i];
          if (typeof handler === 'function') {
            handler.apply(this.el, arguments);
          }
        }
      }
    }]);
  }();
  function wrapFunc(el, handler) {
    var EventshandlerAdmin = new EventsHandlerAdmin(el);
    EventshandlerAdmin.add(handler);
    return EventshandlerAdmin;
  }
  var TouchEvents = function () {
    function TouchEvents(el, option) {
      _classCallCheck(this, TouchEvents);
      this.element = typeof el == 'string' ? document.querySelector(el) : el;
      this.start = this.start.bind(this);
      this.move = this.move.bind(this);
      this.end = this.end.bind(this);
      this.cancel = this.cancel.bind(this);
      this.element.addEventListener('touchstart', this.start, false);
      this.element.addEventListener('touchmove', this.move, false);
      this.element.addEventListener('touchend', this.end, false);
      this.element.addEventListener('touchcancel', this.cancel, false);
      this.preV = {
        x: null,
        y: null
      };
      this.pinchStartLen = null;
      this.zoom = 1;
      this.isDoubleTap = false;
      var noop = function noop() {};
      this.rotate = wrapFunc(this.element, option.rotate || noop);
      this.touchStart = wrapFunc(this.element, option.touchStart || noop);
      this.multipointStart = wrapFunc(this.element, option.multipointStart || noop);
      this.multipointEnd = wrapFunc(this.element, option.multipointEnd || noop);
      this.pinch = wrapFunc(this.element, option.pinch || noop);
      this.swipe = wrapFunc(this.element, option.swipe || noop);
      this.tap = wrapFunc(this.element, option.tap || noop);
      this.doubleTap = wrapFunc(this.element, option.doubleTap || noop);
      this.longTap = wrapFunc(this.element, option.longTap || noop);
      this.singleTap = wrapFunc(this.element, option.singleTap || noop);
      this.pressMove = wrapFunc(this.element, option.pressMove || noop);
      this.twoFingerPressMove = wrapFunc(this.element, option.twoFingerPressMove || noop);
      this.touchMove = wrapFunc(this.element, option.touchMove || noop);
      this.touchEnd = wrapFunc(this.element, option.touchEnd || noop);
      this.touchCancel = wrapFunc(this.element, option.touchCancel || noop);
      this.translateContainer = this.element;
      this._cancelAllHandler = this.cancelAll.bind(this);
      window.addEventListener('scroll', this._cancelAllHandler);
      this.delta = null;
      this.last = null;
      this.now = null;
      this.tapTimeout = null;
      this.singleTapTimeout = null;
      this.longTapTimeout = null;
      this.swipeTimeout = null;
      this.x1 = this.x2 = this.y1 = this.y2 = null;
      this.preTapPosition = {
        x: null,
        y: null
      };
    }
    return _createClass(TouchEvents, [{
      key: "start",
      value: function start(evt) {
        if (!evt.touches) {
          return;
        }
        var ignoreDragFor = ['a', 'button', 'input'];
        if (evt.target && evt.target.nodeName && ignoreDragFor.indexOf(evt.target.nodeName.toLowerCase()) >= 0) {
          console.log('ignore drag for this touched element', evt.target.nodeName.toLowerCase());
          return;
        }
        this.now = Date.now();
        this.x1 = evt.touches[0].pageX;
        this.y1 = evt.touches[0].pageY;
        this.delta = this.now - (this.last || this.now);
        this.touchStart.dispatch(evt, this.element);
        if (this.preTapPosition.x !== null) {
          this.isDoubleTap = this.delta > 0 && this.delta <= 250 && Math.abs(this.preTapPosition.x - this.x1) < 30 && Math.abs(this.preTapPosition.y - this.y1) < 30;
          if (this.isDoubleTap) {
            clearTimeout(this.singleTapTimeout);
          }
        }
        this.preTapPosition.x = this.x1;
        this.preTapPosition.y = this.y1;
        this.last = this.now;
        var preV = this.preV,
          len = evt.touches.length;
        if (len > 1) {
          this._cancelLongTap();
          this._cancelSingleTap();
          var v = {
            x: evt.touches[1].pageX - this.x1,
            y: evt.touches[1].pageY - this.y1
          };
          preV.x = v.x;
          preV.y = v.y;
          this.pinchStartLen = getLen(preV);
          this.multipointStart.dispatch(evt, this.element);
        }
        this._preventTap = false;
        this.longTapTimeout = setTimeout(function () {
          this.longTap.dispatch(evt, this.element);
          this._preventTap = true;
        }.bind(this), 750);
      }
    }, {
      key: "move",
      value: function move(evt) {
        if (!evt.touches) {
          return;
        }
        var preV = this.preV,
          len = evt.touches.length,
          currentX = evt.touches[0].pageX,
          currentY = evt.touches[0].pageY;
        this.isDoubleTap = false;
        if (len > 1) {
          var sCurrentX = evt.touches[1].pageX,
            sCurrentY = evt.touches[1].pageY;
          var v = {
            x: evt.touches[1].pageX - currentX,
            y: evt.touches[1].pageY - currentY
          };
          if (preV.x !== null) {
            if (this.pinchStartLen > 0) {
              evt.zoom = getLen(v) / this.pinchStartLen;
              this.pinch.dispatch(evt, this.element);
            }
            evt.angle = getRotateAngle(v, preV);
            this.rotate.dispatch(evt, this.element);
          }
          preV.x = v.x;
          preV.y = v.y;
          if (this.x2 !== null && this.sx2 !== null) {
            evt.deltaX = (currentX - this.x2 + sCurrentX - this.sx2) / 2;
            evt.deltaY = (currentY - this.y2 + sCurrentY - this.sy2) / 2;
          } else {
            evt.deltaX = 0;
            evt.deltaY = 0;
          }
          this.twoFingerPressMove.dispatch(evt, this.element);
          this.sx2 = sCurrentX;
          this.sy2 = sCurrentY;
        } else {
          if (this.x2 !== null) {
            evt.deltaX = currentX - this.x2;
            evt.deltaY = currentY - this.y2;
            var movedX = Math.abs(this.x1 - this.x2),
              movedY = Math.abs(this.y1 - this.y2);
            if (movedX > 10 || movedY > 10) {
              this._preventTap = true;
            }
          } else {
            evt.deltaX = 0;
            evt.deltaY = 0;
          }
          this.pressMove.dispatch(evt, this.element);
        }
        this.touchMove.dispatch(evt, this.element);
        this._cancelLongTap();
        this.x2 = currentX;
        this.y2 = currentY;
        if (len > 1) {
          evt.preventDefault();
        }
      }
    }, {
      key: "end",
      value: function end(evt) {
        if (!evt.changedTouches) {
          return;
        }
        this._cancelLongTap();
        var self = this;
        if (evt.touches.length < 2) {
          this.multipointEnd.dispatch(evt, this.element);
          this.sx2 = this.sy2 = null;
        }
        if (this.x2 && Math.abs(this.x1 - this.x2) > 30 || this.y2 && Math.abs(this.y1 - this.y2) > 30) {
          evt.direction = this._swipeDirection(this.x1, this.x2, this.y1, this.y2);
          this.swipeTimeout = setTimeout(function () {
            self.swipe.dispatch(evt, self.element);
          }, 0);
        } else {
          this.tapTimeout = setTimeout(function () {
            if (!self._preventTap) {
              self.tap.dispatch(evt, self.element);
            }
            if (self.isDoubleTap) {
              self.doubleTap.dispatch(evt, self.element);
              self.isDoubleTap = false;
            }
          }, 0);
          if (!self.isDoubleTap) {
            self.singleTapTimeout = setTimeout(function () {
              self.singleTap.dispatch(evt, self.element);
            }, 250);
          }
        }
        this.touchEnd.dispatch(evt, this.element);
        this.preV.x = 0;
        this.preV.y = 0;
        this.zoom = 1;
        this.pinchStartLen = null;
        this.x1 = this.x2 = this.y1 = this.y2 = null;
      }
    }, {
      key: "cancelAll",
      value: function cancelAll() {
        this._preventTap = true;
        clearTimeout(this.singleTapTimeout);
        clearTimeout(this.tapTimeout);
        clearTimeout(this.longTapTimeout);
        clearTimeout(this.swipeTimeout);
      }
    }, {
      key: "cancel",
      value: function cancel(evt) {
        this.cancelAll();
        this.touchCancel.dispatch(evt, this.element);
      }
    }, {
      key: "_cancelLongTap",
      value: function _cancelLongTap() {
        clearTimeout(this.longTapTimeout);
      }
    }, {
      key: "_cancelSingleTap",
      value: function _cancelSingleTap() {
        clearTimeout(this.singleTapTimeout);
      }
    }, {
      key: "_swipeDirection",
      value: function _swipeDirection(x1, x2, y1, y2) {
        return Math.abs(x1 - x2) >= Math.abs(y1 - y2) ? x1 - x2 > 0 ? 'Left' : 'Right' : y1 - y2 > 0 ? 'Up' : 'Down';
      }
    }, {
      key: "on",
      value: function on(evt, handler) {
        if (this[evt]) {
          this[evt].add(handler);
        }
      }
    }, {
      key: "off",
      value: function off(evt, handler) {
        if (this[evt]) {
          this[evt].del(handler);
        }
      }
    }, {
      key: "destroy",
      value: function destroy() {
        if (this.singleTapTimeout) {
          clearTimeout(this.singleTapTimeout);
        }
        if (this.tapTimeout) {
          clearTimeout(this.tapTimeout);
        }
        if (this.longTapTimeout) {
          clearTimeout(this.longTapTimeout);
        }
        if (this.swipeTimeout) {
          clearTimeout(this.swipeTimeout);
        }
        this.element.removeEventListener('touchstart', this.start);
        this.element.removeEventListener('touchmove', this.move);
        this.element.removeEventListener('touchend', this.end);
        this.element.removeEventListener('touchcancel', this.cancel);
        this.rotate.del();
        this.touchStart.del();
        this.multipointStart.del();
        this.multipointEnd.del();
        this.pinch.del();
        this.swipe.del();
        this.tap.del();
        this.doubleTap.del();
        this.longTap.del();
        this.singleTap.del();
        this.pressMove.del();
        this.twoFingerPressMove.del();
        this.touchMove.del();
        this.touchEnd.del();
        this.touchCancel.del();
        this.preV = this.pinchStartLen = this.zoom = this.isDoubleTap = this.delta = this.last = this.now = this.tapTimeout = this.singleTapTimeout = this.longTapTimeout = this.swipeTimeout = this.x1 = this.x2 = this.y1 = this.y2 = this.preTapPosition = this.rotate = this.touchStart = this.multipointStart = this.multipointEnd = this.pinch = this.swipe = this.tap = this.doubleTap = this.longTap = this.singleTap = this.pressMove = this.touchMove = this.touchEnd = this.touchCancel = this.twoFingerPressMove = null;
        window.removeEventListener('scroll', this._cancelAllHandler);
        return null;
      }
    }]);
  }();

  function resetSlideMove(slide) {
    var transitionEnd = whichTransitionEvent();
    var windowWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
    var media = hasClass(slide, 'gslide-media') ? slide : slide.querySelector('.gslide-media');
    var container = closest(media, '.ginner-container');
    var desc = slide.querySelector('.gslide-description');
    if (windowWidth > 769) {
      media = container;
    }
    addClass(media, 'greset');
    cssTransform(media, 'translate3d(0, 0, 0)');
    addEvent(transitionEnd, {
      onElement: media,
      once: true,
      withCallback: function withCallback(event, target) {
        removeClass(media, 'greset');
      }
    });
    media.style.opacity = '';
    if (desc) {
      desc.style.opacity = '';
    }
  }
  function touchNavigation(instance) {
    if (instance.events.hasOwnProperty('touch')) {
      return false;
    }
    var winSize = windowSize();
    var winWidth = winSize.width;
    var winHeight = winSize.height;
    var process = false;
    var currentSlide = null;
    var media = null;
    var mediaImage = null;
    var doingMove = false;
    var initScale = 1;
    var maxScale = 4.5;
    var currentScale = 1;
    var doingZoom = false;
    var imageZoomed = false;
    var zoomedPosX = null;
    var zoomedPosY = null;
    var lastZoomedPosX = null;
    var lastZoomedPosY = null;
    var hDistance;
    var vDistance;
    var hDistancePercent = 0;
    var vDistancePercent = 0;
    var vSwipe = false;
    var hSwipe = false;
    var startCoords = {};
    var endCoords = {};
    var xDown = 0;
    var yDown = 0;
    var isInlined;
    var sliderWrapper = document.getElementById('glightbox-slider');
    var overlay = document.querySelector('.goverlay');
    var touchInstance = new TouchEvents(sliderWrapper, {
      touchStart: function touchStart(e) {
        process = true;
        if (hasClass(e.targetTouches[0].target, 'ginner-container') || closest(e.targetTouches[0].target, '.gslide-desc') || e.targetTouches[0].target.nodeName.toLowerCase() == 'a') {
          process = false;
        }
        if (closest(e.targetTouches[0].target, '.gslide-inline') && !hasClass(e.targetTouches[0].target.parentNode, 'gslide-inline')) {
          process = false;
        }
        if (process) {
          endCoords = e.targetTouches[0];
          startCoords.pageX = e.targetTouches[0].pageX;
          startCoords.pageY = e.targetTouches[0].pageY;
          xDown = e.targetTouches[0].clientX;
          yDown = e.targetTouches[0].clientY;
          currentSlide = instance.activeSlide;
          media = currentSlide.querySelector('.gslide-media');
          isInlined = currentSlide.querySelector('.gslide-inline');
          mediaImage = null;
          if (hasClass(media, 'gslide-image')) {
            mediaImage = media.querySelector('img');
          }
          var windowWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
          if (windowWidth > 769) {
            media = currentSlide.querySelector('.ginner-container');
          }
          removeClass(overlay, 'greset');
          if (e.pageX > 20 && e.pageX < window.innerWidth - 20) {
            return;
          }
          e.preventDefault();
        }
      },
      touchMove: function touchMove(e) {
        if (!process) {
          return;
        }
        endCoords = e.targetTouches[0];
        if (doingZoom || imageZoomed) {
          return;
        }
        if (isInlined && isInlined.offsetHeight > winHeight) {
          var moved = startCoords.pageX - endCoords.pageX;
          if (Math.abs(moved) <= 13) {
            return false;
          }
        }
        doingMove = true;
        var xUp = e.targetTouches[0].clientX;
        var yUp = e.targetTouches[0].clientY;
        var xDiff = xDown - xUp;
        var yDiff = yDown - yUp;
        if (Math.abs(xDiff) > Math.abs(yDiff)) {
          vSwipe = false;
          hSwipe = true;
        } else {
          hSwipe = false;
          vSwipe = true;
        }
        hDistance = endCoords.pageX - startCoords.pageX;
        hDistancePercent = hDistance * 100 / winWidth;
        vDistance = endCoords.pageY - startCoords.pageY;
        vDistancePercent = vDistance * 100 / winHeight;
        var opacity;
        if (vSwipe && mediaImage) {
          opacity = 1 - Math.abs(vDistance) / winHeight;
          overlay.style.opacity = opacity;
          if (instance.settings.touchFollowAxis) {
            hDistancePercent = 0;
          }
        }
        if (hSwipe) {
          opacity = 1 - Math.abs(hDistance) / winWidth;
          media.style.opacity = opacity;
          if (instance.settings.touchFollowAxis) {
            vDistancePercent = 0;
          }
        }
        if (!mediaImage) {
          return cssTransform(media, "translate3d(".concat(hDistancePercent, "%, 0, 0)"));
        }
        cssTransform(media, "translate3d(".concat(hDistancePercent, "%, ").concat(vDistancePercent, "%, 0)"));
      },
      touchEnd: function touchEnd() {
        if (!process) {
          return;
        }
        doingMove = false;
        if (imageZoomed || doingZoom) {
          lastZoomedPosX = zoomedPosX;
          lastZoomedPosY = zoomedPosY;
          return;
        }
        var v = Math.abs(parseInt(vDistancePercent));
        var h = Math.abs(parseInt(hDistancePercent));
        if (v > 29 && mediaImage) {
          instance.close();
          return;
        }
        if (v < 29 && h < 25) {
          addClass(overlay, 'greset');
          overlay.style.opacity = 1;
          return resetSlideMove(media);
        }
      },
      multipointEnd: function multipointEnd() {
        setTimeout(function () {
          doingZoom = false;
        }, 50);
      },
      multipointStart: function multipointStart() {
        doingZoom = true;
        initScale = currentScale ? currentScale : 1;
      },
      pinch: function pinch(evt) {
        if (!mediaImage || doingMove) {
          return false;
        }
        doingZoom = true;
        mediaImage.scaleX = mediaImage.scaleY = initScale * evt.zoom;
        var scale = initScale * evt.zoom;
        imageZoomed = true;
        if (scale <= 1) {
          imageZoomed = false;
          scale = 1;
          lastZoomedPosY = null;
          lastZoomedPosX = null;
          zoomedPosX = null;
          zoomedPosY = null;
          mediaImage.setAttribute('style', '');
          return;
        }
        if (scale > maxScale) {
          scale = maxScale;
        }
        mediaImage.style.transform = "scale3d(".concat(scale, ", ").concat(scale, ", 1)");
        currentScale = scale;
      },
      pressMove: function pressMove(e) {
        if (imageZoomed && !doingZoom) {
          var mhDistance = endCoords.pageX - startCoords.pageX;
          var mvDistance = endCoords.pageY - startCoords.pageY;
          if (lastZoomedPosX) {
            mhDistance = mhDistance + lastZoomedPosX;
          }
          if (lastZoomedPosY) {
            mvDistance = mvDistance + lastZoomedPosY;
          }
          zoomedPosX = mhDistance;
          zoomedPosY = mvDistance;
          var style = "translate3d(".concat(mhDistance, "px, ").concat(mvDistance, "px, 0)");
          if (currentScale) {
            style += " scale3d(".concat(currentScale, ", ").concat(currentScale, ", 1)");
          }
          cssTransform(mediaImage, style);
        }
      },
      swipe: function swipe(evt) {
        if (imageZoomed) {
          return;
        }
        if (doingZoom) {
          doingZoom = false;
          return;
        }
        if (evt.direction == 'Left') {
          if (instance.index == instance.elements.length - 1) {
            return resetSlideMove(media);
          }
          instance.nextSlide();
        }
        if (evt.direction == 'Right') {
          if (instance.index == 0) {
            return resetSlideMove(media);
          }
          instance.prevSlide();
        }
      }
    });
    instance.events['touch'] = touchInstance;
  }

  var _version = '3.3.1';
  var isMobile$1 = isMobile();
  var isTouch$1 = isTouch();
  var html = document.getElementsByTagName('html')[0];
  var defaults = {
    selector: '.glightbox',
    elements: null,
    skin: 'clean',
    theme: 'clean',
    closeButton: true,
    startAt: null,
    autoplayVideos: true,
    autofocusVideos: true,
    descPosition: 'bottom',
    width: '900px',
    height: '506px',
    videosWidth: '960px',
    beforeSlideChange: null,
    afterSlideChange: null,
    beforeSlideLoad: null,
    afterSlideLoad: null,
    slideInserted: null,
    slideRemoved: null,
    slideExtraAttributes: null,
    onOpen: null,
    onClose: null,
    loop: false,
    zoomable: true,
    draggable: true,
    dragAutoSnap: false,
    dragToleranceX: 40,
    dragToleranceY: 65,
    preload: true,
    oneSlidePerOpen: false,
    touchNavigation: true,
    touchFollowAxis: true,
    keyboardNavigation: true,
    closeOnOutsideClick: true,
    plugins: false,
    plyr: {
      css: 'https://cdn.plyr.io/3.6.12/plyr.css',
      js: 'https://cdn.plyr.io/3.6.12/plyr.js',
      config: {
        ratio: '16:9',
        fullscreen: {
          enabled: true,
          iosNative: true
        },
        youtube: {
          noCookie: true,
          rel: 0,
          showinfo: 0,
          iv_load_policy: 3
        },
        vimeo: {
          byline: false,
          portrait: false,
          title: false,
          transparent: false
        }
      }
    },
    openEffect: 'zoom',
    closeEffect: 'zoom',
    slideEffect: 'slide',
    moreText: 'See more',
    moreLength: 60,
    cssEfects: {
      fade: {
        "in": 'fadeIn',
        out: 'fadeOut'
      },
      zoom: {
        "in": 'zoomIn',
        out: 'zoomOut'
      },
      slide: {
        "in": 'slideInRight',
        out: 'slideOutLeft'
      },
      slideBack: {
        "in": 'slideInLeft',
        out: 'slideOutRight'
      },
      none: {
        "in": 'none',
        out: 'none'
      }
    },
    svg: {
      close: '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 512 512" xml:space="preserve"><g><g><path d="M505.943,6.058c-8.077-8.077-21.172-8.077-29.249,0L6.058,476.693c-8.077,8.077-8.077,21.172,0,29.249C10.096,509.982,15.39,512,20.683,512c5.293,0,10.586-2.019,14.625-6.059L505.943,35.306C514.019,27.23,514.019,14.135,505.943,6.058z"/></g></g><g><g><path d="M505.942,476.694L35.306,6.059c-8.076-8.077-21.172-8.077-29.248,0c-8.077,8.076-8.077,21.171,0,29.248l470.636,470.636c4.038,4.039,9.332,6.058,14.625,6.058c5.293,0,10.587-2.019,14.624-6.057C514.018,497.866,514.018,484.771,505.942,476.694z"/></g></g></svg>',
      next: '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 477.175 477.175" xml:space="preserve"> <g><path d="M360.731,229.075l-225.1-225.1c-5.3-5.3-13.8-5.3-19.1,0s-5.3,13.8,0,19.1l215.5,215.5l-215.5,215.5c-5.3,5.3-5.3,13.8,0,19.1c2.6,2.6,6.1,4,9.5,4c3.4,0,6.9-1.3,9.5-4l225.1-225.1C365.931,242.875,365.931,234.275,360.731,229.075z"/></g></svg>',
      prev: '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 477.175 477.175" xml:space="preserve"><g><path d="M145.188,238.575l215.5-215.5c5.3-5.3,5.3-13.8,0-19.1s-13.8-5.3-19.1,0l-225.1,225.1c-5.3,5.3-5.3,13.8,0,19.1l225.1,225c2.6,2.6,6.1,4,9.5,4s6.9-1.3,9.5-4c5.3-5.3,5.3-13.8,0-19.1L145.188,238.575z"/></g></svg>'
    }
  };
  defaults.slideHTML = "<div class=\"gslide\">\n    <div class=\"gslide-inner-content\">\n        <div class=\"ginner-container\">\n            <div class=\"gslide-media\">\n            </div>\n            <div class=\"gslide-description\">\n                <div class=\"gdesc-inner\">\n                    <h4 class=\"gslide-title\"></h4>\n                    <div class=\"gslide-desc\"></div>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>";
  defaults.lightboxHTML = "<div id=\"glightbox-body\" class=\"glightbox-container\" tabindex=\"-1\" role=\"dialog\" aria-hidden=\"false\">\n    <div class=\"gloader visible\"></div>\n    <div class=\"goverlay\"></div>\n    <div class=\"gcontainer\">\n    <div id=\"glightbox-slider\" class=\"gslider\"></div>\n    <button class=\"gclose gbtn\" aria-label=\"Close\" data-taborder=\"3\">{closeSVG}</button>\n    <button class=\"gprev gbtn\" aria-label=\"Previous\" data-taborder=\"2\">{prevSVG}</button>\n    <button class=\"gnext gbtn\" aria-label=\"Next\" data-taborder=\"1\">{nextSVG}</button>\n</div>\n</div>";
  var GlightboxInit = function () {
    function GlightboxInit() {
      var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
      _classCallCheck(this, GlightboxInit);
      this.customOptions = options;
      this.settings = extend(defaults, options);
      this.effectsClasses = this.getAnimationClasses();
      this.videoPlayers = {};
      this.apiEvents = [];
      this.fullElementsList = false;
    }
    return _createClass(GlightboxInit, [{
      key: "init",
      value: function init() {
        var _this = this;
        var selector = this.getSelector();
        if (selector) {
          this.baseEvents = addEvent('click', {
            onElement: selector,
            withCallback: function withCallback(e, target) {
              e.preventDefault();
              _this.open(target);
            }
          });
        }
        this.elements = this.getElements();
      }
    }, {
      key: "open",
      value: function open() {
        var element = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
        var startAt = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
        if (this.elements.length === 0) {
          return false;
        }
        this.activeSlide = null;
        this.prevActiveSlideIndex = null;
        this.prevActiveSlide = null;
        var index = isNumber(startAt) ? startAt : this.settings.startAt;
        if (isNode(element)) {
          var gallery = element.getAttribute('data-gallery');
          if (gallery) {
            this.fullElementsList = this.elements;
            this.elements = this.getGalleryElements(this.elements, gallery);
          }
          if (isNil(index)) {
            index = this.getElementIndex(element);
            if (index < 0) {
              index = 0;
            }
          }
        }
        if (!isNumber(index)) {
          index = 0;
        }
        this.build();
        animateElement(this.overlay, this.settings.openEffect === 'none' ? 'none' : this.settings.cssEfects.fade["in"]);
        var body = document.body;
        var scrollBar = window.innerWidth - document.documentElement.clientWidth;
        if (scrollBar > 0) {
          var styleSheet = document.createElement('style');
          styleSheet.type = 'text/css';
          styleSheet.className = 'gcss-styles';
          styleSheet.innerText = ".gscrollbar-fixer {margin-right: ".concat(scrollBar, "px}");
          document.head.appendChild(styleSheet);
          addClass(body, 'gscrollbar-fixer');
        }
        addClass(body, 'glightbox-open');
        addClass(html, 'glightbox-open');
        if (isMobile$1) {
          addClass(document.body, 'glightbox-mobile');
          this.settings.slideEffect = 'slide';
        }
        this.showSlide(index, true);
        if (this.elements.length === 1) {
          addClass(this.prevButton, 'glightbox-button-hidden');
          addClass(this.nextButton, 'glightbox-button-hidden');
        } else {
          removeClass(this.prevButton, 'glightbox-button-hidden');
          removeClass(this.nextButton, 'glightbox-button-hidden');
        }
        this.lightboxOpen = true;
        this.trigger('open');
        if (isFunction(this.settings.onOpen)) {
          this.settings.onOpen();
        }
        if (isTouch$1 && this.settings.touchNavigation) {
          touchNavigation(this);
        }
        if (this.settings.keyboardNavigation) {
          keyboardNavigation(this);
        }
      }
    }, {
      key: "openAt",
      value: function openAt() {
        var index = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 0;
        this.open(null, index);
      }
    }, {
      key: "showSlide",
      value: function showSlide() {
        var _this2 = this;
        var index = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : 0;
        var first = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : false;
        show(this.loader);
        this.index = parseInt(index);
        var current = this.slidesContainer.querySelector('.current');
        if (current) {
          removeClass(current, 'current');
        }
        this.slideAnimateOut();
        var slideNode = this.slidesContainer.querySelectorAll('.gslide')[index];
        if (hasClass(slideNode, 'loaded')) {
          this.slideAnimateIn(slideNode, first);
          hide(this.loader);
        } else {
          show(this.loader);
          var slide = this.elements[index];
          var slideData = {
            index: this.index,
            slide: slideNode,
            slideNode: slideNode,
            slideConfig: slide.slideConfig,
            slideIndex: this.index,
            trigger: slide.node,
            player: null
          };
          this.trigger('slide_before_load', slideData);
          slide.instance.setContent(slideNode, function () {
            hide(_this2.loader);
            _this2.resize();
            _this2.slideAnimateIn(slideNode, first);
            _this2.trigger('slide_after_load', slideData);
          });
        }
        this.slideDescription = slideNode.querySelector('.gslide-description');
        this.slideDescriptionContained = this.slideDescription && hasClass(this.slideDescription.parentNode, 'gslide-media');
        if (this.settings.preload) {
          this.preloadSlide(index + 1);
          this.preloadSlide(index - 1);
        }
        this.updateNavigationClasses();
        this.activeSlide = slideNode;
      }
    }, {
      key: "preloadSlide",
      value: function preloadSlide(index) {
        var _this3 = this;
        if (index < 0 || index > this.elements.length - 1) {
          return false;
        }
        if (isNil(this.elements[index])) {
          return false;
        }
        var slideNode = this.slidesContainer.querySelectorAll('.gslide')[index];
        if (hasClass(slideNode, 'loaded')) {
          return false;
        }
        var slide = this.elements[index];
        var type = slide.type;
        var slideData = {
          index: index,
          slide: slideNode,
          slideNode: slideNode,
          slideConfig: slide.slideConfig,
          slideIndex: index,
          trigger: slide.node,
          player: null
        };
        this.trigger('slide_before_load', slideData);
        if (type === 'video' || type === 'external') {
          setTimeout(function () {
            slide.instance.setContent(slideNode, function () {
              _this3.trigger('slide_after_load', slideData);
            });
          }, 200);
        } else {
          slide.instance.setContent(slideNode, function () {
            _this3.trigger('slide_after_load', slideData);
          });
        }
      }
    }, {
      key: "prevSlide",
      value: function prevSlide() {
        this.goToSlide(this.index - 1);
      }
    }, {
      key: "nextSlide",
      value: function nextSlide() {
        this.goToSlide(this.index + 1);
      }
    }, {
      key: "goToSlide",
      value: function goToSlide() {
        var index = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;
        this.prevActiveSlide = this.activeSlide;
        this.prevActiveSlideIndex = this.index;
        if (!this.loop() && (index < 0 || index > this.elements.length - 1)) {
          return false;
        }
        if (index < 0) {
          index = this.elements.length - 1;
        } else if (index >= this.elements.length) {
          index = 0;
        }
        this.showSlide(index);
      }
    }, {
      key: "insertSlide",
      value: function insertSlide() {
        var config = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
        var index = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : -1;
        if (index < 0) {
          index = this.elements.length;
        }
        var slide = new Slide(config, this, index);
        var data = slide.getConfig();
        var slideInfo = extend({}, data);
        var newSlide = slide.create();
        var totalSlides = this.elements.length - 1;
        slideInfo.index = index;
        slideInfo.node = false;
        slideInfo.instance = slide;
        slideInfo.slideConfig = data;
        this.elements.splice(index, 0, slideInfo);
        var addedSlideNode = null;
        var addedSlidePlayer = null;
        if (this.slidesContainer) {
          if (index > totalSlides) {
            this.slidesContainer.appendChild(newSlide);
          } else {
            var existingSlide = this.slidesContainer.querySelectorAll('.gslide')[index];
            this.slidesContainer.insertBefore(newSlide, existingSlide);
          }
          if (this.settings.preload && this.index == 0 && index == 0 || this.index - 1 == index || this.index + 1 == index) {
            this.preloadSlide(index);
          }
          if (this.index === 0 && index === 0) {
            this.index = 1;
          }
          this.updateNavigationClasses();
          addedSlideNode = this.slidesContainer.querySelectorAll('.gslide')[index];
          addedSlidePlayer = this.getSlidePlayerInstance(index);
          slideInfo.slideNode = addedSlideNode;
        }
        this.trigger('slide_inserted', {
          index: index,
          slide: addedSlideNode,
          slideNode: addedSlideNode,
          slideConfig: data,
          slideIndex: index,
          trigger: null,
          player: addedSlidePlayer
        });
        if (isFunction(this.settings.slideInserted)) {
          this.settings.slideInserted({
            index: index,
            slide: addedSlideNode,
            player: addedSlidePlayer
          });
        }
      }
    }, {
      key: "removeSlide",
      value: function removeSlide() {
        var index = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : -1;
        if (index < 0 || index > this.elements.length - 1) {
          return false;
        }
        var slide = this.slidesContainer && this.slidesContainer.querySelectorAll('.gslide')[index];
        if (slide) {
          if (this.getActiveSlideIndex() == index) {
            if (index == this.elements.length - 1) {
              this.prevSlide();
            } else {
              this.nextSlide();
            }
          }
          slide.parentNode.removeChild(slide);
        }
        this.elements.splice(index, 1);
        this.trigger('slide_removed', index);
        if (isFunction(this.settings.slideRemoved)) {
          this.settings.slideRemoved(index);
        }
      }
    }, {
      key: "slideAnimateIn",
      value: function slideAnimateIn(slide, first) {
        var _this4 = this;
        var slideMedia = slide.querySelector('.gslide-media');
        var slideDesc = slide.querySelector('.gslide-description');
        var prevData = {
          index: this.prevActiveSlideIndex,
          slide: this.prevActiveSlide,
          slideNode: this.prevActiveSlide,
          slideIndex: this.prevActiveSlide,
          slideConfig: isNil(this.prevActiveSlideIndex) ? null : this.elements[this.prevActiveSlideIndex].slideConfig,
          trigger: isNil(this.prevActiveSlideIndex) ? null : this.elements[this.prevActiveSlideIndex].node,
          player: this.getSlidePlayerInstance(this.prevActiveSlideIndex)
        };
        var nextData = {
          index: this.index,
          slide: this.activeSlide,
          slideNode: this.activeSlide,
          slideConfig: this.elements[this.index].slideConfig,
          slideIndex: this.index,
          trigger: this.elements[this.index].node,
          player: this.getSlidePlayerInstance(this.index)
        };
        if (slideMedia.offsetWidth > 0 && slideDesc) {
          hide(slideDesc);
          slideDesc.style.display = '';
        }
        removeClass(slide, this.effectsClasses);
        if (first) {
          animateElement(slide, this.settings.cssEfects[this.settings.openEffect]["in"], function () {
            if (_this4.settings.autoplayVideos) {
              _this4.slidePlayerPlay(slide);
            }
            _this4.trigger('slide_changed', {
              prev: prevData,
              current: nextData
            });
            if (isFunction(_this4.settings.afterSlideChange)) {
              _this4.settings.afterSlideChange.apply(_this4, [prevData, nextData]);
            }
          });
        } else {
          var effectName = this.settings.slideEffect;
          var animIn = effectName !== 'none' ? this.settings.cssEfects[effectName]["in"] : effectName;
          if (this.prevActiveSlideIndex > this.index) {
            if (this.settings.slideEffect == 'slide') {
              animIn = this.settings.cssEfects.slideBack["in"];
            }
          }
          animateElement(slide, animIn, function () {
            if (_this4.settings.autoplayVideos) {
              _this4.slidePlayerPlay(slide);
            }
            _this4.trigger('slide_changed', {
              prev: prevData,
              current: nextData
            });
            if (isFunction(_this4.settings.afterSlideChange)) {
              _this4.settings.afterSlideChange.apply(_this4, [prevData, nextData]);
            }
          });
        }
        setTimeout(function () {
          _this4.resize(slide);
        }, 100);
        addClass(slide, 'current');
      }
    }, {
      key: "slideAnimateOut",
      value: function slideAnimateOut() {
        if (!this.prevActiveSlide) {
          return false;
        }
        var prevSlide = this.prevActiveSlide;
        removeClass(prevSlide, this.effectsClasses);
        addClass(prevSlide, 'prev');
        var animation = this.settings.slideEffect;
        var animOut = animation !== 'none' ? this.settings.cssEfects[animation].out : animation;
        this.slidePlayerPause(prevSlide);
        this.trigger('slide_before_change', {
          prev: {
            index: this.prevActiveSlideIndex,
            slide: this.prevActiveSlide,
            slideNode: this.prevActiveSlide,
            slideIndex: this.prevActiveSlideIndex,
            slideConfig: isNil(this.prevActiveSlideIndex) ? null : this.elements[this.prevActiveSlideIndex].slideConfig,
            trigger: isNil(this.prevActiveSlideIndex) ? null : this.elements[this.prevActiveSlideIndex].node,
            player: this.getSlidePlayerInstance(this.prevActiveSlideIndex)
          },
          current: {
            index: this.index,
            slide: this.activeSlide,
            slideNode: this.activeSlide,
            slideIndex: this.index,
            slideConfig: this.elements[this.index].slideConfig,
            trigger: this.elements[this.index].node,
            player: this.getSlidePlayerInstance(this.index)
          }
        });
        if (isFunction(this.settings.beforeSlideChange)) {
          this.settings.beforeSlideChange.apply(this, [{
            index: this.prevActiveSlideIndex,
            slide: this.prevActiveSlide,
            player: this.getSlidePlayerInstance(this.prevActiveSlideIndex)
          }, {
            index: this.index,
            slide: this.activeSlide,
            player: this.getSlidePlayerInstance(this.index)
          }]);
        }
        if (this.prevActiveSlideIndex > this.index && this.settings.slideEffect == 'slide') {
          animOut = this.settings.cssEfects.slideBack.out;
        }
        animateElement(prevSlide, animOut, function () {
          var container = prevSlide.querySelector('.ginner-container');
          var media = prevSlide.querySelector('.gslide-media');
          var desc = prevSlide.querySelector('.gslide-description');
          container.style.transform = '';
          media.style.transform = '';
          removeClass(media, 'greset');
          media.style.opacity = '';
          if (desc) {
            desc.style.opacity = '';
          }
          removeClass(prevSlide, 'prev');
        });
      }
    }, {
      key: "getAllPlayers",
      value: function getAllPlayers() {
        return this.videoPlayers;
      }
    }, {
      key: "getSlidePlayerInstance",
      value: function getSlidePlayerInstance(index) {
        var id = 'gvideo' + index;
        var videoPlayers = this.getAllPlayers();
        if (has(videoPlayers, id) && videoPlayers[id]) {
          return videoPlayers[id];
        }
        return false;
      }
    }, {
      key: "stopSlideVideo",
      value: function stopSlideVideo(slide) {
        if (isNode(slide)) {
          var node = slide.querySelector('.gvideo-wrapper');
          if (node) {
            slide = node.getAttribute('data-index');
          }
        }
        console.log('stopSlideVideo is deprecated, use slidePlayerPause');
        var player = this.getSlidePlayerInstance(slide);
        if (player && player.playing) {
          player.pause();
        }
      }
    }, {
      key: "slidePlayerPause",
      value: function slidePlayerPause(slide) {
        if (isNode(slide)) {
          var node = slide.querySelector('.gvideo-wrapper');
          if (node) {
            slide = node.getAttribute('data-index');
          }
        }
        var player = this.getSlidePlayerInstance(slide);
        if (player && player.playing) {
          player.pause();
        }
      }
    }, {
      key: "playSlideVideo",
      value: function playSlideVideo(slide) {
        if (isNode(slide)) {
          var node = slide.querySelector('.gvideo-wrapper');
          if (node) {
            slide = node.getAttribute('data-index');
          }
        }
        console.log('playSlideVideo is deprecated, use slidePlayerPlay');
        var player = this.getSlidePlayerInstance(slide);
        if (player && !player.playing) {
          player.play();
        }
      }
    }, {
      key: "slidePlayerPlay",
      value: function slidePlayerPlay(slide) {
        var _this$settings$plyr$c;
        if (isMobile$1 && !((_this$settings$plyr$c = this.settings.plyr.config) !== null && _this$settings$plyr$c !== void 0 && _this$settings$plyr$c.muted)) {
          return;
        }
        if (isNode(slide)) {
          var node = slide.querySelector('.gvideo-wrapper');
          if (node) {
            slide = node.getAttribute('data-index');
          }
        }
        var player = this.getSlidePlayerInstance(slide);
        if (player && !player.playing) {
          player.play();
          if (this.settings.autofocusVideos) {
            player.elements.container.focus();
          }
        }
      }
    }, {
      key: "setElements",
      value: function setElements(elements) {
        var _this5 = this;
        this.settings.elements = false;
        var newElements = [];
        if (elements && elements.length) {
          each(elements, function (el, i) {
            var slide = new Slide(el, _this5, i);
            var data = slide.getConfig();
            var slideInfo = extend({}, data);
            slideInfo.slideConfig = data;
            slideInfo.instance = slide;
            slideInfo.index = i;
            newElements.push(slideInfo);
          });
        }
        this.elements = newElements;
        if (this.lightboxOpen) {
          this.slidesContainer.innerHTML = '';
          if (this.elements.length) {
            each(this.elements, function () {
              var slide = createHTML(_this5.settings.slideHTML);
              _this5.slidesContainer.appendChild(slide);
            });
            this.showSlide(0, true);
          }
        }
      }
    }, {
      key: "getElementIndex",
      value: function getElementIndex(node) {
        var index = false;
        each(this.elements, function (el, i) {
          if (has(el, 'node') && el.node == node) {
            index = i;
            return true;
          }
        });
        return index;
      }
    }, {
      key: "getElements",
      value: function getElements() {
        var _this6 = this;
        var list = [];
        this.elements = this.elements ? this.elements : [];
        if (!isNil(this.settings.elements) && isArray(this.settings.elements) && this.settings.elements.length) {
          each(this.settings.elements, function (el, i) {
            var slide = new Slide(el, _this6, i);
            var elData = slide.getConfig();
            var slideInfo = extend({}, elData);
            slideInfo.node = false;
            slideInfo.index = i;
            slideInfo.instance = slide;
            slideInfo.slideConfig = elData;
            list.push(slideInfo);
          });
        }
        var nodes = false;
        var selector = this.getSelector();
        if (selector) {
          nodes = document.querySelectorAll(this.getSelector());
        }
        if (!nodes) {
          return list;
        }
        each(nodes, function (el, i) {
          var slide = new Slide(el, _this6, i);
          var elData = slide.getConfig();
          var slideInfo = extend({}, elData);
          slideInfo.node = el;
          slideInfo.index = i;
          slideInfo.instance = slide;
          slideInfo.slideConfig = elData;
          slideInfo.gallery = el.getAttribute('data-gallery');
          list.push(slideInfo);
        });
        return list;
      }
    }, {
      key: "getGalleryElements",
      value: function getGalleryElements(list, gallery) {
        return list.filter(function (el) {
          return el.gallery == gallery;
        });
      }
    }, {
      key: "getSelector",
      value: function getSelector() {
        if (this.settings.elements) {
          return false;
        }
        if (this.settings.selector && this.settings.selector.substring(0, 5) == 'data-') {
          return "*[".concat(this.settings.selector, "]");
        }
        return this.settings.selector;
      }
    }, {
      key: "getActiveSlide",
      value: function getActiveSlide() {
        return this.slidesContainer.querySelectorAll('.gslide')[this.index];
      }
    }, {
      key: "getActiveSlideIndex",
      value: function getActiveSlideIndex() {
        return this.index;
      }
    }, {
      key: "getAnimationClasses",
      value: function getAnimationClasses() {
        var effects = [];
        for (var key in this.settings.cssEfects) {
          if (this.settings.cssEfects.hasOwnProperty(key)) {
            var effect = this.settings.cssEfects[key];
            effects.push("g".concat(effect["in"]));
            effects.push("g".concat(effect.out));
          }
        }
        return effects.join(' ');
      }
    }, {
      key: "build",
      value: function build() {
        var _this7 = this;
        if (this.built) {
          return false;
        }
        var children = document.body.childNodes;
        var bodyChildElms = [];
        each(children, function (el) {
          if (el.parentNode == document.body && el.nodeName.charAt(0) !== '#' && el.hasAttribute && !el.hasAttribute('aria-hidden')) {
            bodyChildElms.push(el);
            el.setAttribute('aria-hidden', 'true');
          }
        });
        var nextSVG = has(this.settings.svg, 'next') ? this.settings.svg.next : '';
        var prevSVG = has(this.settings.svg, 'prev') ? this.settings.svg.prev : '';
        var closeSVG = has(this.settings.svg, 'close') ? this.settings.svg.close : '';
        var lightboxHTML = this.settings.lightboxHTML;
        lightboxHTML = lightboxHTML.replace(/{nextSVG}/g, nextSVG);
        lightboxHTML = lightboxHTML.replace(/{prevSVG}/g, prevSVG);
        lightboxHTML = lightboxHTML.replace(/{closeSVG}/g, closeSVG);
        lightboxHTML = createHTML(lightboxHTML);
        document.body.appendChild(lightboxHTML);
        var modal = document.getElementById('glightbox-body');
        this.modal = modal;
        var closeButton = modal.querySelector('.gclose');
        this.prevButton = modal.querySelector('.gprev');
        this.nextButton = modal.querySelector('.gnext');
        this.overlay = modal.querySelector('.goverlay');
        this.loader = modal.querySelector('.gloader');
        this.slidesContainer = document.getElementById('glightbox-slider');
        this.bodyHiddenChildElms = bodyChildElms;
        this.events = {};
        addClass(this.modal, 'glightbox-' + this.settings.skin);
        if (this.settings.closeButton && closeButton) {
          this.events['close'] = addEvent('click', {
            onElement: closeButton,
            withCallback: function withCallback(e, target) {
              e.preventDefault();
              _this7.close();
            }
          });
        }
        if (closeButton && !this.settings.closeButton) {
          closeButton.parentNode.removeChild(closeButton);
        }
        if (this.nextButton) {
          this.events['next'] = addEvent('click', {
            onElement: this.nextButton,
            withCallback: function withCallback(e, target) {
              e.preventDefault();
              _this7.nextSlide();
            }
          });
        }
        if (this.prevButton) {
          this.events['prev'] = addEvent('click', {
            onElement: this.prevButton,
            withCallback: function withCallback(e, target) {
              e.preventDefault();
              _this7.prevSlide();
            }
          });
        }
        if (this.settings.closeOnOutsideClick) {
          this.events['outClose'] = addEvent('click', {
            onElement: modal,
            withCallback: function withCallback(e, target) {
              if (!_this7.preventOutsideClick && !hasClass(document.body, 'glightbox-mobile') && !closest(e.target, '.ginner-container')) {
                if (!closest(e.target, '.gbtn') && !hasClass(e.target, 'gnext') && !hasClass(e.target, 'gprev')) {
                  _this7.close();
                }
              }
            }
          });
        }
        each(this.elements, function (slide, i) {
          _this7.slidesContainer.appendChild(slide.instance.create());
          slide.slideNode = _this7.slidesContainer.querySelectorAll('.gslide')[i];
        });
        if (isTouch$1) {
          addClass(document.body, 'glightbox-touch');
        }
        this.events['resize'] = addEvent('resize', {
          onElement: window,
          withCallback: function withCallback() {
            _this7.resize();
          }
        });
        this.built = true;
      }
    }, {
      key: "resize",
      value: function resize() {
        var slide = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : null;
        slide = !slide ? this.activeSlide : slide;
        if (!slide || hasClass(slide, 'zoomed')) {
          return;
        }
        var winSize = windowSize();
        var video = slide.querySelector('.gvideo-wrapper');
        var image = slide.querySelector('.gslide-image');
        var description = this.slideDescription;
        var winWidth = winSize.width;
        var winHeight = winSize.height;
        if (winWidth <= 768) {
          addClass(document.body, 'glightbox-mobile');
        } else {
          removeClass(document.body, 'glightbox-mobile');
        }
        if (!video && !image) {
          return;
        }
        var descriptionResize = false;
        if (description && (hasClass(description, 'description-bottom') || hasClass(description, 'description-top')) && !hasClass(description, 'gabsolute')) {
          descriptionResize = true;
        }
        if (image) {
          if (winWidth <= 768) {
            var imgNode = image.querySelector('img');
          } else if (descriptionResize) {
            var _this$elements$this$i;
            var descHeight = description.offsetHeight;
            var _imgNode = image.querySelector('img');
            var slideTriggerNode = (_this$elements$this$i = this.elements[this.index]) === null || _this$elements$this$i === void 0 ? void 0 : _this$elements$this$i.node;
            var maxHeightValue = '100vh';
            if (slideTriggerNode) {
              var _slideTriggerNode$get;
              maxHeightValue = (_slideTriggerNode$get = slideTriggerNode.getAttribute('data-height')) !== null && _slideTriggerNode$get !== void 0 ? _slideTriggerNode$get : maxHeightValue;
            }
            _imgNode.setAttribute('style', "max-height: calc(".concat(maxHeightValue, " - ").concat(descHeight, "px)"));
            description.setAttribute('style', "max-width: ".concat(_imgNode.offsetWidth, "px;"));
          }
        }
        if (video) {
          var ratio = has(this.settings.plyr.config, 'ratio') ? this.settings.plyr.config.ratio : '';
          if (!ratio) {
            var containerWidth = video.clientWidth;
            var containerHeight = video.clientHeight;
            var divisor = containerWidth / containerHeight;
            ratio = "".concat(containerWidth / divisor, ":").concat(containerHeight / divisor);
          }
          var videoRatio = ratio.split(':');
          var videoWidth = this.settings.videosWidth;
          var maxWidth = this.settings.videosWidth;
          if (isNumber(videoWidth) || videoWidth.indexOf('px') !== -1) {
            maxWidth = parseInt(videoWidth);
          } else {
            if (videoWidth.indexOf('vw') !== -1) {
              maxWidth = winWidth * parseInt(videoWidth) / 100;
            } else if (videoWidth.indexOf('vh') !== -1) {
              maxWidth = winHeight * parseInt(videoWidth) / 100;
            } else if (videoWidth.indexOf('%') !== -1) {
              maxWidth = winWidth * parseInt(videoWidth) / 100;
            } else {
              maxWidth = parseInt(video.clientWidth);
            }
          }
          var maxHeight = maxWidth / (parseInt(videoRatio[0]) / parseInt(videoRatio[1]));
          maxHeight = Math.floor(maxHeight);
          if (descriptionResize) {
            winHeight = winHeight - description.offsetHeight;
          }
          if (maxWidth > winWidth || maxHeight > winHeight || winHeight < maxHeight && winWidth > maxWidth) {
            var vwidth = video.offsetWidth;
            var vheight = video.offsetHeight;
            var _ratio = winHeight / vheight;
            var vsize = {
              width: vwidth * _ratio,
              height: vheight * _ratio
            };
            video.parentNode.setAttribute('style', "max-width: ".concat(vsize.width, "px"));
            if (descriptionResize) {
              description.setAttribute('style', "max-width: ".concat(vsize.width, "px;"));
            }
          } else {
            video.parentNode.style.maxWidth = "".concat(videoWidth);
            if (descriptionResize) {
              description.setAttribute('style', "max-width: ".concat(videoWidth, ";"));
            }
          }
        }
      }
    }, {
      key: "reload",
      value: function reload() {
        this.init();
      }
    }, {
      key: "updateNavigationClasses",
      value: function updateNavigationClasses() {
        var loop = this.loop();
        removeClass(this.nextButton, 'disabled');
        removeClass(this.prevButton, 'disabled');
        if (this.index == 0 && this.elements.length - 1 == 0) {
          addClass(this.prevButton, 'disabled');
          addClass(this.nextButton, 'disabled');
        } else if (this.index === 0 && !loop) {
          addClass(this.prevButton, 'disabled');
        } else if (this.index === this.elements.length - 1 && !loop) {
          addClass(this.nextButton, 'disabled');
        }
      }
    }, {
      key: "loop",
      value: function loop() {
        var loop = has(this.settings, 'loopAtEnd') ? this.settings.loopAtEnd : null;
        loop = has(this.settings, 'loop') ? this.settings.loop : loop;
        return loop;
      }
    }, {
      key: "close",
      value: function close() {
        var _this8 = this;
        if (!this.lightboxOpen) {
          if (this.events) {
            for (var key in this.events) {
              if (this.events.hasOwnProperty(key)) {
                this.events[key].destroy();
              }
            }
            this.events = null;
          }
          return false;
        }
        if (this.closing) {
          return false;
        }
        this.closing = true;
        this.slidePlayerPause(this.activeSlide);
        if (this.fullElementsList) {
          this.elements = this.fullElementsList;
        }
        if (this.bodyHiddenChildElms.length) {
          each(this.bodyHiddenChildElms, function (el) {
            el.removeAttribute('aria-hidden');
          });
        }
        addClass(this.modal, 'glightbox-closing');
        animateElement(this.overlay, this.settings.openEffect == 'none' ? 'none' : this.settings.cssEfects.fade.out);
        animateElement(this.activeSlide, this.settings.cssEfects[this.settings.closeEffect].out, function () {
          _this8.activeSlide = null;
          _this8.prevActiveSlideIndex = null;
          _this8.prevActiveSlide = null;
          _this8.built = false;
          if (_this8.events) {
            for (var _key in _this8.events) {
              if (_this8.events.hasOwnProperty(_key)) {
                _this8.events[_key].destroy();
              }
            }
            _this8.events = null;
          }
          var body = document.body;
          removeClass(html, 'glightbox-open');
          removeClass(body, 'glightbox-open touching gdesc-open glightbox-touch glightbox-mobile gscrollbar-fixer');
          _this8.modal.parentNode.removeChild(_this8.modal);
          _this8.trigger('close');
          if (isFunction(_this8.settings.onClose)) {
            _this8.settings.onClose();
          }
          var styles = document.querySelector('.gcss-styles');
          if (styles) {
            styles.parentNode.removeChild(styles);
          }
          _this8.lightboxOpen = false;
          _this8.closing = null;
        });
      }
    }, {
      key: "destroy",
      value: function destroy() {
        this.close();
        this.clearAllEvents();
        if (this.baseEvents) {
          this.baseEvents.destroy();
        }
      }
    }, {
      key: "on",
      value: function on(evt, callback) {
        var once = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : false;
        if (!evt || !isFunction(callback)) {
          throw new TypeError('Event name and callback must be defined');
        }
        this.apiEvents.push({
          evt: evt,
          once: once,
          callback: callback
        });
      }
    }, {
      key: "once",
      value: function once(evt, callback) {
        this.on(evt, callback, true);
      }
    }, {
      key: "trigger",
      value: function trigger(eventName) {
        var _this9 = this;
        var data = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
        var onceTriggered = [];
        each(this.apiEvents, function (event, i) {
          var evt = event.evt,
            once = event.once,
            callback = event.callback;
          if (evt == eventName) {
            callback(data);
            if (once) {
              onceTriggered.push(i);
            }
          }
        });
        if (onceTriggered.length) {
          each(onceTriggered, function (i) {
            return _this9.apiEvents.splice(i, 1);
          });
        }
      }
    }, {
      key: "clearAllEvents",
      value: function clearAllEvents() {
        this.apiEvents.splice(0, this.apiEvents.length);
      }
    }, {
      key: "version",
      value: function version() {
        return _version;
      }
    }]);
  }();
  function glightbox () {
    var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
    var instance = new GlightboxInit(options);
    instance.init();
    return instance;
  }

  return glightbox;

})));

/*! For license information please see choices.min.js.LICENSE.txt */
!function(){"use strict";var e={282:function(e,t,i){Object.defineProperty(t,"__esModule",{value:!0}),t.clearChoices=t.activateChoices=t.filterChoices=t.addChoice=void 0;var n=i(883);t.addChoice=function(e){var t=e.value,i=e.label,r=e.id,s=e.groupId,o=e.disabled,a=e.elementId,c=e.customProperties,l=e.placeholder,h=e.keyCode;return{type:n.ACTION_TYPES.ADD_CHOICE,value:t,label:i,id:r,groupId:s,disabled:o,elementId:a,customProperties:c,placeholder:l,keyCode:h}},t.filterChoices=function(e){return{type:n.ACTION_TYPES.FILTER_CHOICES,results:e}},t.activateChoices=function(e){return void 0===e&&(e=!0),{type:n.ACTION_TYPES.ACTIVATE_CHOICES,active:e}},t.clearChoices=function(){return{type:n.ACTION_TYPES.CLEAR_CHOICES}}},783:function(e,t,i){Object.defineProperty(t,"__esModule",{value:!0}),t.addGroup=void 0;var n=i(883);t.addGroup=function(e){var t=e.value,i=e.id,r=e.active,s=e.disabled;return{type:n.ACTION_TYPES.ADD_GROUP,value:t,id:i,active:r,disabled:s}}},464:function(e,t,i){Object.defineProperty(t,"__esModule",{value:!0}),t.highlightItem=t.removeItem=t.addItem=void 0;var n=i(883);t.addItem=function(e){var t=e.value,i=e.label,r=e.id,s=e.choiceId,o=e.groupId,a=e.customProperties,c=e.placeholder,l=e.keyCode;return{type:n.ACTION_TYPES.ADD_ITEM,value:t,label:i,id:r,choiceId:s,groupId:o,customProperties:a,placeholder:c,keyCode:l}},t.removeItem=function(e,t){return{type:n.ACTION_TYPES.REMOVE_ITEM,id:e,choiceId:t}},t.highlightItem=function(e,t){return{type:n.ACTION_TYPES.HIGHLIGHT_ITEM,id:e,highlighted:t}}},137:function(e,t,i){Object.defineProperty(t,"__esModule",{value:!0}),t.setIsLoading=t.resetTo=t.clearAll=void 0;var n=i(883);t.clearAll=function(){return{type:n.ACTION_TYPES.CLEAR_ALL}},t.resetTo=function(e){return{type:n.ACTION_TYPES.RESET_TO,state:e}},t.setIsLoading=function(e){return{type:n.ACTION_TYPES.SET_IS_LOADING,isLoading:e}}},373:function(e,t,i){var n=this&&this.__spreadArray||function(e,t,i){if(i||2===arguments.length)for(var n,r=0,s=t.length;r<s;r++)!n&&r in t||(n||(n=Array.prototype.slice.call(t,0,r)),n[r]=t[r]);return e.concat(n||Array.prototype.slice.call(t))},r=this&&this.__importDefault||function(e){return e&&e.__esModule?e:{default:e}};Object.defineProperty(t,"__esModule",{value:!0});var s=r(i(996)),o=r(i(221)),a=i(282),c=i(783),l=i(464),h=i(137),u=i(520),d=i(883),p=i(789),f=i(799),m=i(655),v=r(i(744)),g=r(i(686)),_="-ms-scroll-limit"in document.documentElement.style&&"-ms-ime-align"in document.documentElement.style,y={},E=function(){function e(t,i){void 0===t&&(t="[data-choice]"),void 0===i&&(i={});var r=this;void 0===i.allowHTML&&console.warn("Deprecation warning: allowHTML will default to false in a future release. To render HTML in Choices, you will need to set it to true. Setting allowHTML will suppress this message."),this.config=s.default.all([p.DEFAULT_CONFIG,e.defaults.options,i],{arrayMerge:function(e,t){return n([],t,!0)}});var o=(0,f.diff)(this.config,p.DEFAULT_CONFIG);o.length&&console.warn("Unknown config option(s) passed",o.join(", "));var a="string"==typeof t?document.querySelector(t):t;if(!(a instanceof HTMLInputElement||a instanceof HTMLSelectElement))throw TypeError("Expected one of the following types text|select-one|select-multiple");if(this._isTextElement=a.type===d.TEXT_TYPE,this._isSelectOneElement=a.type===d.SELECT_ONE_TYPE,this._isSelectMultipleElement=a.type===d.SELECT_MULTIPLE_TYPE,this._isSelectElement=this._isSelectOneElement||this._isSelectMultipleElement,this.config.searchEnabled=this._isSelectMultipleElement||this.config.searchEnabled,["auto","always"].includes("".concat(this.config.renderSelectedChoices))||(this.config.renderSelectedChoices="auto"),i.addItemFilter&&"function"!=typeof i.addItemFilter){var c=i.addItemFilter instanceof RegExp?i.addItemFilter:new RegExp(i.addItemFilter);this.config.addItemFilter=c.test.bind(c)}if(this._isTextElement?this.passedElement=new u.WrappedInput({element:a,classNames:this.config.classNames,delimiter:this.config.delimiter}):this.passedElement=new u.WrappedSelect({element:a,classNames:this.config.classNames,template:function(e){return r._templates.option(e)}}),this.initialised=!1,this._store=new v.default,this._initialState=m.defaultState,this._currentState=m.defaultState,this._prevState=m.defaultState,this._currentValue="",this._canSearch=!!this.config.searchEnabled,this._isScrollingOnIe=!1,this._highlightPosition=0,this._wasTap=!0,this._placeholderValue=this._generatePlaceholderValue(),this._baseId=(0,f.generateId)(this.passedElement.element,"choices-"),this._direction=this.passedElement.dir,!this._direction){var l=window.getComputedStyle(this.passedElement.element).direction;l!==window.getComputedStyle(document.documentElement).direction&&(this._direction=l)}if(this._idNames={itemChoice:"item-choice"},this._isSelectElement&&(this._presetGroups=this.passedElement.optionGroups,this._presetOptions=this.passedElement.options),this._presetChoices=this.config.choices,this._presetItems=this.config.items,this.passedElement.value&&this._isTextElement){var h=this.passedElement.value.split(this.config.delimiter);this._presetItems=this._presetItems.concat(h)}if(this.passedElement.options&&this.passedElement.options.forEach((function(e){r._presetChoices.push({value:e.value,label:e.innerHTML,selected:!!e.selected,disabled:e.disabled||e.parentNode.disabled,placeholder:""===e.value||e.hasAttribute("placeholder"),customProperties:(0,f.parseCustomProperties)(e.dataset.customProperties)})})),this._render=this._render.bind(this),this._onFocus=this._onFocus.bind(this),this._onBlur=this._onBlur.bind(this),this._onKeyUp=this._onKeyUp.bind(this),this._onKeyDown=this._onKeyDown.bind(this),this._onClick=this._onClick.bind(this),this._onTouchMove=this._onTouchMove.bind(this),this._onTouchEnd=this._onTouchEnd.bind(this),this._onMouseDown=this._onMouseDown.bind(this),this._onMouseOver=this._onMouseOver.bind(this),this._onFormReset=this._onFormReset.bind(this),this._onSelectKey=this._onSelectKey.bind(this),this._onEnterKey=this._onEnterKey.bind(this),this._onEscapeKey=this._onEscapeKey.bind(this),this._onDirectionKey=this._onDirectionKey.bind(this),this._onDeleteKey=this._onDeleteKey.bind(this),this.passedElement.isActive)return this.config.silent||console.warn("Trying to initialise Choices on element already initialised",{element:t}),void(this.initialised=!0);this.init()}return Object.defineProperty(e,"defaults",{get:function(){return Object.preventExtensions({get options(){return y},get templates(){return g.default}})},enumerable:!1,configurable:!0}),e.prototype.init=function(){if(!this.initialised){this._createTemplates(),this._createElements(),this._createStructure(),this._store.subscribe(this._render),this._render(),this._addEventListeners(),(!this.config.addItems||this.passedElement.element.hasAttribute("disabled"))&&this.disable(),this.initialised=!0;var e=this.config.callbackOnInit;e&&"function"==typeof e&&e.call(this)}},e.prototype.destroy=function(){this.initialised&&(this._removeEventListeners(),this.passedElement.reveal(),this.containerOuter.unwrap(this.passedElement.element),this.clearStore(),this._isSelectElement&&(this.passedElement.options=this._presetOptions),this._templates=g.default,this.initialised=!1)},e.prototype.enable=function(){return this.passedElement.isDisabled&&this.passedElement.enable(),this.containerOuter.isDisabled&&(this._addEventListeners(),this.input.enable(),this.containerOuter.enable()),this},e.prototype.disable=function(){return this.passedElement.isDisabled||this.passedElement.disable(),this.containerOuter.isDisabled||(this._removeEventListeners(),this.input.disable(),this.containerOuter.disable()),this},e.prototype.highlightItem=function(e,t){if(void 0===t&&(t=!0),!e||!e.id)return this;var i=e.id,n=e.groupId,r=void 0===n?-1:n,s=e.value,o=void 0===s?"":s,a=e.label,c=void 0===a?"":a,h=r>=0?this._store.getGroupById(r):null;return this._store.dispatch((0,l.highlightItem)(i,!0)),t&&this.passedElement.triggerEvent(d.EVENTS.highlightItem,{id:i,value:o,label:c,groupValue:h&&h.value?h.value:null}),this},e.prototype.unhighlightItem=function(e){if(!e||!e.id)return this;var t=e.id,i=e.groupId,n=void 0===i?-1:i,r=e.value,s=void 0===r?"":r,o=e.label,a=void 0===o?"":o,c=n>=0?this._store.getGroupById(n):null;return this._store.dispatch((0,l.highlightItem)(t,!1)),this.passedElement.triggerEvent(d.EVENTS.highlightItem,{id:t,value:s,label:a,groupValue:c&&c.value?c.value:null}),this},e.prototype.highlightAll=function(){var e=this;return this._store.items.forEach((function(t){return e.highlightItem(t)})),this},e.prototype.unhighlightAll=function(){var e=this;return this._store.items.forEach((function(t){return e.unhighlightItem(t)})),this},e.prototype.removeActiveItemsByValue=function(e){var t=this;return this._store.activeItems.filter((function(t){return t.value===e})).forEach((function(e){return t._removeItem(e)})),this},e.prototype.removeActiveItems=function(e){var t=this;return this._store.activeItems.filter((function(t){return t.id!==e})).forEach((function(e){return t._removeItem(e)})),this},e.prototype.removeHighlightedItems=function(e){var t=this;return void 0===e&&(e=!1),this._store.highlightedActiveItems.forEach((function(i){t._removeItem(i),e&&t._triggerChange(i.value)})),this},e.prototype.showDropdown=function(e){var t=this;return this.dropdown.isActive||requestAnimationFrame((function(){t.dropdown.show(),t.containerOuter.open(t.dropdown.distanceFromTopWindow),!e&&t._canSearch&&t.input.focus(),t.passedElement.triggerEvent(d.EVENTS.showDropdown,{})})),this},e.prototype.hideDropdown=function(e){var t=this;return this.dropdown.isActive?(requestAnimationFrame((function(){t.dropdown.hide(),t.containerOuter.close(),!e&&t._canSearch&&(t.input.removeActiveDescendant(),t.input.blur()),t.passedElement.triggerEvent(d.EVENTS.hideDropdown,{})})),this):this},e.prototype.getValue=function(e){void 0===e&&(e=!1);var t=this._store.activeItems.reduce((function(t,i){var n=e?i.value:i;return t.push(n),t}),[]);return this._isSelectOneElement?t[0]:t},e.prototype.setValue=function(e){var t=this;return this.initialised?(e.forEach((function(e){return t._setChoiceOrItem(e)})),this):this},e.prototype.setChoiceByValue=function(e){var t=this;return!this.initialised||this._isTextElement||(Array.isArray(e)?e:[e]).forEach((function(e){return t._findAndSelectChoiceByValue(e)})),this},e.prototype.setChoices=function(e,t,i,n){var r=this;if(void 0===e&&(e=[]),void 0===t&&(t="value"),void 0===i&&(i="label"),void 0===n&&(n=!1),!this.initialised)throw new ReferenceError("setChoices was called on a non-initialized instance of Choices");if(!this._isSelectElement)throw new TypeError("setChoices can't be used with INPUT based Choices");if("string"!=typeof t||!t)throw new TypeError("value parameter must be a name of 'value' field in passed objects");if(n&&this.clearChoices(),"function"==typeof e){var s=e(this);if("function"==typeof Promise&&s instanceof Promise)return new Promise((function(e){return requestAnimationFrame(e)})).then((function(){return r._handleLoadingState(!0)})).then((function(){return s})).then((function(e){return r.setChoices(e,t,i,n)})).catch((function(e){r.config.silent||console.error(e)})).then((function(){return r._handleLoadingState(!1)})).then((function(){return r}));if(!Array.isArray(s))throw new TypeError(".setChoices first argument function must return either array of choices or Promise, got: ".concat(typeof s));return this.setChoices(s,t,i,!1)}if(!Array.isArray(e))throw new TypeError(".setChoices must be called either with array of choices with a function resulting into Promise of array of choices");return this.containerOuter.removeLoadingState(),this._startLoading(),e.forEach((function(e){if(e.choices)r._addGroup({id:e.id?parseInt("".concat(e.id),10):null,group:e,valueKey:t,labelKey:i});else{var n=e;r._addChoice({value:n[t],label:n[i],isSelected:!!n.selected,isDisabled:!!n.disabled,placeholder:!!n.placeholder,customProperties:n.customProperties})}})),this._stopLoading(),this},e.prototype.clearChoices=function(){return this._store.dispatch((0,a.clearChoices)()),this},e.prototype.clearStore=function(){return this._store.dispatch((0,h.clearAll)()),this},e.prototype.clearInput=function(){var e=!this._isSelectOneElement;return this.input.clear(e),!this._isTextElement&&this._canSearch&&(this._isSearching=!1,this._store.dispatch((0,a.activateChoices)(!0))),this},e.prototype._render=function(){if(!this._store.isLoading()){this._currentState=this._store.state;var e=this._currentState.choices!==this._prevState.choices||this._currentState.groups!==this._prevState.groups||this._currentState.items!==this._prevState.items,t=this._isSelectElement,i=this._currentState.items!==this._prevState.items;e&&(t&&this._renderChoices(),i&&this._renderItems(),this._prevState=this._currentState)}},e.prototype._renderChoices=function(){var e=this,t=this._store,i=t.activeGroups,n=t.activeChoices,r=document.createDocumentFragment();if(this.choiceList.clear(),this.config.resetScrollPosition&&requestAnimationFrame((function(){return e.choiceList.scrollToTop()})),i.length>=1&&!this._isSearching){var s=n.filter((function(e){return!0===e.placeholder&&-1===e.groupId}));s.length>=1&&(r=this._createChoicesFragment(s,r)),r=this._createGroupsFragment(i,n,r)}else n.length>=1&&(r=this._createChoicesFragment(n,r));if(r.childNodes&&r.childNodes.length>0){var o=this._store.activeItems,a=this._canAddItem(o,this.input.value);if(a.response)this.choiceList.append(r),this._highlightChoice();else{var c=this._getTemplate("notice",a.notice);this.choiceList.append(c)}}else{var l=void 0;c=void 0,this._isSearching?(c="function"==typeof this.config.noResultsText?this.config.noResultsText():this.config.noResultsText,l=this._getTemplate("notice",c,"no-results")):(c="function"==typeof this.config.noChoicesText?this.config.noChoicesText():this.config.noChoicesText,l=this._getTemplate("notice",c,"no-choices")),this.choiceList.append(l)}},e.prototype._renderItems=function(){var e=this._store.activeItems||[];this.itemList.clear();var t=this._createItemsFragment(e);t.childNodes&&this.itemList.append(t)},e.prototype._createGroupsFragment=function(e,t,i){var n=this;return void 0===i&&(i=document.createDocumentFragment()),this.config.shouldSort&&e.sort(this.config.sorter),e.forEach((function(e){var r=function(e){return t.filter((function(t){return n._isSelectOneElement?t.groupId===e.id:t.groupId===e.id&&("always"===n.config.renderSelectedChoices||!t.selected)}))}(e);if(r.length>=1){var s=n._getTemplate("choiceGroup",e);i.appendChild(s),n._createChoicesFragment(r,i,!0)}})),i},e.prototype._createChoicesFragment=function(e,t,i){var r=this;void 0===t&&(t=document.createDocumentFragment()),void 0===i&&(i=!1);var s=this.config,o=s.renderSelectedChoices,a=s.searchResultLimit,c=s.renderChoiceLimit,l=this._isSearching?f.sortByScore:this.config.sorter,h=function(e){if("auto"!==o||r._isSelectOneElement||!e.selected){var i=r._getTemplate("choice",e,r.config.itemSelectText);t.appendChild(i)}},u=e;"auto"!==o||this._isSelectOneElement||(u=e.filter((function(e){return!e.selected})));var d=u.reduce((function(e,t){return t.placeholder?e.placeholderChoices.push(t):e.normalChoices.push(t),e}),{placeholderChoices:[],normalChoices:[]}),p=d.placeholderChoices,m=d.normalChoices;(this.config.shouldSort||this._isSearching)&&m.sort(l);var v=u.length,g=this._isSelectOneElement?n(n([],p,!0),m,!0):m;this._isSearching?v=a:c&&c>0&&!i&&(v=c);for(var _=0;_<v;_+=1)g[_]&&h(g[_]);return t},e.prototype._createItemsFragment=function(e,t){var i=this;void 0===t&&(t=document.createDocumentFragment());var n=this.config,r=n.shouldSortItems,s=n.sorter,o=n.removeItemButton;return r&&!this._isSelectOneElement&&e.sort(s),this._isTextElement?this.passedElement.value=e.map((function(e){return e.value})).join(this.config.delimiter):this.passedElement.options=e,e.forEach((function(e){var n=i._getTemplate("item",e,o);t.appendChild(n)})),t},e.prototype._triggerChange=function(e){null!=e&&this.passedElement.triggerEvent(d.EVENTS.change,{value:e})},e.prototype._selectPlaceholderChoice=function(e){this._addItem({value:e.value,label:e.label,choiceId:e.id,groupId:e.groupId,placeholder:e.placeholder}),this._triggerChange(e.value)},e.prototype._handleButtonAction=function(e,t){if(e&&t&&this.config.removeItems&&this.config.removeItemButton){var i=t.parentNode&&t.parentNode.dataset.id,n=i&&e.find((function(e){return e.id===parseInt(i,10)}));n&&(this._removeItem(n),this._triggerChange(n.value),this._isSelectOneElement&&this._store.placeholderChoice&&this._selectPlaceholderChoice(this._store.placeholderChoice))}},e.prototype._handleItemAction=function(e,t,i){var n=this;if(void 0===i&&(i=!1),e&&t&&this.config.removeItems&&!this._isSelectOneElement){var r=t.dataset.id;e.forEach((function(e){e.id!==parseInt("".concat(r),10)||e.highlighted?!i&&e.highlighted&&n.unhighlightItem(e):n.highlightItem(e)})),this.input.focus()}},e.prototype._handleChoiceAction=function(e,t){if(e&&t){var i=t.dataset.id,n=i&&this._store.getChoiceById(i);if(n){var r=e[0]&&e[0].keyCode?e[0].keyCode:void 0,s=this.dropdown.isActive;n.keyCode=r,this.passedElement.triggerEvent(d.EVENTS.choice,{choice:n}),n.selected||n.disabled||this._canAddItem(e,n.value).response&&(this._addItem({value:n.value,label:n.label,choiceId:n.id,groupId:n.groupId,customProperties:n.customProperties,placeholder:n.placeholder,keyCode:n.keyCode}),this._triggerChange(n.value)),this.clearInput(),s&&this._isSelectOneElement&&(this.hideDropdown(!0),this.containerOuter.focus())}}},e.prototype._handleBackspace=function(e){if(this.config.removeItems&&e){var t=e[e.length-1],i=e.some((function(e){return e.highlighted}));this.config.editItems&&!i&&t?(this.input.value=t.value,this.input.setWidth(),this._removeItem(t),this._triggerChange(t.value)):(i||this.highlightItem(t,!1),this.removeHighlightedItems(!0))}},e.prototype._startLoading=function(){this._store.dispatch((0,h.setIsLoading)(!0))},e.prototype._stopLoading=function(){this._store.dispatch((0,h.setIsLoading)(!1))},e.prototype._handleLoadingState=function(e){void 0===e&&(e=!0);var t=this.itemList.getChild(".".concat(this.config.classNames.placeholder));e?(this.disable(),this.containerOuter.addLoadingState(),this._isSelectOneElement?t?t.innerHTML=this.config.loadingText:(t=this._getTemplate("placeholder",this.config.loadingText))&&this.itemList.append(t):this.input.placeholder=this.config.loadingText):(this.enable(),this.containerOuter.removeLoadingState(),this._isSelectOneElement?t&&(t.innerHTML=this._placeholderValue||""):this.input.placeholder=this._placeholderValue||"")},e.prototype._handleSearch=function(e){if(this.input.isFocussed){var t=this._store.choices,i=this.config,n=i.searchFloor,r=i.searchChoices,s=t.some((function(e){return!e.active}));if(null!=e&&e.length>=n){var o=r?this._searchChoices(e):0;this.passedElement.triggerEvent(d.EVENTS.search,{value:e,resultCount:o})}else s&&(this._isSearching=!1,this._store.dispatch((0,a.activateChoices)(!0)))}},e.prototype._canAddItem=function(e,t){var i=!0,n="function"==typeof this.config.addItemText?this.config.addItemText(t):this.config.addItemText;if(!this._isSelectOneElement){var r=(0,f.existsInArray)(e,t);this.config.maxItemCount>0&&this.config.maxItemCount<=e.length&&(i=!1,n="function"==typeof this.config.maxItemText?this.config.maxItemText(this.config.maxItemCount):this.config.maxItemText),!this.config.duplicateItemsAllowed&&r&&i&&(i=!1,n="function"==typeof this.config.uniqueItemText?this.config.uniqueItemText(t):this.config.uniqueItemText),this._isTextElement&&this.config.addItems&&i&&"function"==typeof this.config.addItemFilter&&!this.config.addItemFilter(t)&&(i=!1,n="function"==typeof this.config.customAddItemText?this.config.customAddItemText(t):this.config.customAddItemText)}return{response:i,notice:n}},e.prototype._searchChoices=function(e){var t="string"==typeof e?e.trim():e,i="string"==typeof this._currentValue?this._currentValue.trim():this._currentValue;if(t.length<1&&t==="".concat(i," "))return 0;var r=this._store.searchableChoices,s=t,c=Object.assign(this.config.fuseOptions,{keys:n([],this.config.searchFields,!0),includeMatches:!0}),l=new o.default(r,c).search(s);return this._currentValue=t,this._highlightPosition=0,this._isSearching=!0,this._store.dispatch((0,a.filterChoices)(l)),l.length},e.prototype._addEventListeners=function(){var e=document.documentElement;e.addEventListener("touchend",this._onTouchEnd,!0),this.containerOuter.element.addEventListener("keydown",this._onKeyDown,!0),this.containerOuter.element.addEventListener("mousedown",this._onMouseDown,!0),e.addEventListener("click",this._onClick,{passive:!0}),e.addEventListener("touchmove",this._onTouchMove,{passive:!0}),this.dropdown.element.addEventListener("mouseover",this._onMouseOver,{passive:!0}),this._isSelectOneElement&&(this.containerOuter.element.addEventListener("focus",this._onFocus,{passive:!0}),this.containerOuter.element.addEventListener("blur",this._onBlur,{passive:!0})),this.input.element.addEventListener("keyup",this._onKeyUp,{passive:!0}),this.input.element.addEventListener("focus",this._onFocus,{passive:!0}),this.input.element.addEventListener("blur",this._onBlur,{passive:!0}),this.input.element.form&&this.input.element.form.addEventListener("reset",this._onFormReset,{passive:!0}),this.input.addEventListeners()},e.prototype._removeEventListeners=function(){var e=document.documentElement;e.removeEventListener("touchend",this._onTouchEnd,!0),this.containerOuter.element.removeEventListener("keydown",this._onKeyDown,!0),this.containerOuter.element.removeEventListener("mousedown",this._onMouseDown,!0),e.removeEventListener("click",this._onClick),e.removeEventListener("touchmove",this._onTouchMove),this.dropdown.element.removeEventListener("mouseover",this._onMouseOver),this._isSelectOneElement&&(this.containerOuter.element.removeEventListener("focus",this._onFocus),this.containerOuter.element.removeEventListener("blur",this._onBlur)),this.input.element.removeEventListener("keyup",this._onKeyUp),this.input.element.removeEventListener("focus",this._onFocus),this.input.element.removeEventListener("blur",this._onBlur),this.input.element.form&&this.input.element.form.removeEventListener("reset",this._onFormReset),this.input.removeEventListeners()},e.prototype._onKeyDown=function(e){var t=e.keyCode,i=this._store.activeItems,n=this.input.isFocussed,r=this.dropdown.isActive,s=this.itemList.hasChildren(),o=String.fromCharCode(t),a=/[^\x00-\x1F]/.test(o),c=d.KEY_CODES.BACK_KEY,l=d.KEY_CODES.DELETE_KEY,h=d.KEY_CODES.ENTER_KEY,u=d.KEY_CODES.A_KEY,p=d.KEY_CODES.ESC_KEY,f=d.KEY_CODES.UP_KEY,m=d.KEY_CODES.DOWN_KEY,v=d.KEY_CODES.PAGE_UP_KEY,g=d.KEY_CODES.PAGE_DOWN_KEY;switch(this._isTextElement||r||!a||(this.showDropdown(),this.input.isFocussed||(this.input.value+=e.key.toLowerCase())),t){case u:return this._onSelectKey(e,s);case h:return this._onEnterKey(e,i,r);case p:return this._onEscapeKey(r);case f:case v:case m:case g:return this._onDirectionKey(e,r);case l:case c:return this._onDeleteKey(e,i,n)}},e.prototype._onKeyUp=function(e){var t=e.target,i=e.keyCode,n=this.input.value,r=this._store.activeItems,s=this._canAddItem(r,n),o=d.KEY_CODES.BACK_KEY,c=d.KEY_CODES.DELETE_KEY;if(this._isTextElement)if(s.notice&&n){var l=this._getTemplate("notice",s.notice);this.dropdown.element.innerHTML=l.outerHTML,this.showDropdown(!0)}else this.hideDropdown(!0);else{var h=(i===o||i===c)&&t&&!t.value,u=!this._isTextElement&&this._isSearching,p=this._canSearch&&s.response;h&&u?(this._isSearching=!1,this._store.dispatch((0,a.activateChoices)(!0))):p&&this._handleSearch(this.input.rawValue)}this._canSearch=this.config.searchEnabled},e.prototype._onSelectKey=function(e,t){var i=e.ctrlKey,n=e.metaKey;(i||n)&&t&&(this._canSearch=!1,this.config.removeItems&&!this.input.value&&this.input.element===document.activeElement&&this.highlightAll())},e.prototype._onEnterKey=function(e,t,i){var n=e.target,r=d.KEY_CODES.ENTER_KEY,s=n&&n.hasAttribute("data-button");if(this._isTextElement&&n&&n.value){var o=this.input.value;this._canAddItem(t,o).response&&(this.hideDropdown(!0),this._addItem({value:o}),this._triggerChange(o),this.clearInput())}if(s&&(this._handleButtonAction(t,n),e.preventDefault()),i){var a=this.dropdown.getChild(".".concat(this.config.classNames.highlightedState));a&&(t[0]&&(t[0].keyCode=r),this._handleChoiceAction(t,a)),e.preventDefault()}else this._isSelectOneElement&&(this.showDropdown(),e.preventDefault())},e.prototype._onEscapeKey=function(e){e&&(this.hideDropdown(!0),this.containerOuter.focus())},e.prototype._onDirectionKey=function(e,t){var i=e.keyCode,n=e.metaKey,r=d.KEY_CODES.DOWN_KEY,s=d.KEY_CODES.PAGE_UP_KEY,o=d.KEY_CODES.PAGE_DOWN_KEY;if(t||this._isSelectOneElement){this.showDropdown(),this._canSearch=!1;var a=i===r||i===o?1:-1,c="[data-choice-selectable]",l=void 0;if(n||i===o||i===s)l=a>0?this.dropdown.element.querySelector("".concat(c,":last-of-type")):this.dropdown.element.querySelector(c);else{var h=this.dropdown.element.querySelector(".".concat(this.config.classNames.highlightedState));l=h?(0,f.getAdjacentEl)(h,c,a):this.dropdown.element.querySelector(c)}l&&((0,f.isScrolledIntoView)(l,this.choiceList.element,a)||this.choiceList.scrollToChildElement(l,a),this._highlightChoice(l)),e.preventDefault()}},e.prototype._onDeleteKey=function(e,t,i){var n=e.target;this._isSelectOneElement||n.value||!i||(this._handleBackspace(t),e.preventDefault())},e.prototype._onTouchMove=function(){this._wasTap&&(this._wasTap=!1)},e.prototype._onTouchEnd=function(e){var t=(e||e.touches[0]).target;this._wasTap&&this.containerOuter.element.contains(t)&&((t===this.containerOuter.element||t===this.containerInner.element)&&(this._isTextElement?this.input.focus():this._isSelectMultipleElement&&this.showDropdown()),e.stopPropagation()),this._wasTap=!0},e.prototype._onMouseDown=function(e){var t=e.target;if(t instanceof HTMLElement){if(_&&this.choiceList.element.contains(t)){var i=this.choiceList.element.firstElementChild,n="ltr"===this._direction?e.offsetX>=i.offsetWidth:e.offsetX<i.offsetLeft;this._isScrollingOnIe=n}if(t!==this.input.element){var r=t.closest("[data-button],[data-item],[data-choice]");if(r instanceof HTMLElement){var s=e.shiftKey,o=this._store.activeItems,a=r.dataset;"button"in a?this._handleButtonAction(o,r):"item"in a?this._handleItemAction(o,r,s):"choice"in a&&this._handleChoiceAction(o,r)}e.preventDefault()}}},e.prototype._onMouseOver=function(e){var t=e.target;t instanceof HTMLElement&&"choice"in t.dataset&&this._highlightChoice(t)},e.prototype._onClick=function(e){var t=e.target;this.containerOuter.element.contains(t)?this.dropdown.isActive||this.containerOuter.isDisabled?this._isSelectOneElement&&t!==this.input.element&&!this.dropdown.element.contains(t)&&this.hideDropdown():this._isTextElement?document.activeElement!==this.input.element&&this.input.focus():(this.showDropdown(),this.containerOuter.focus()):(this._store.highlightedActiveItems.length>0&&this.unhighlightAll(),this.containerOuter.removeFocusState(),this.hideDropdown(!0))},e.prototype._onFocus=function(e){var t,i=this,n=e.target;n&&this.containerOuter.element.contains(n)&&((t={})[d.TEXT_TYPE]=function(){n===i.input.element&&i.containerOuter.addFocusState()},t[d.SELECT_ONE_TYPE]=function(){i.containerOuter.addFocusState(),n===i.input.element&&i.showDropdown(!0)},t[d.SELECT_MULTIPLE_TYPE]=function(){n===i.input.element&&(i.showDropdown(!0),i.containerOuter.addFocusState())},t)[this.passedElement.element.type]()},e.prototype._onBlur=function(e){var t,i=this,n=e.target;if(n&&this.containerOuter.element.contains(n)&&!this._isScrollingOnIe){var r=this._store.activeItems.some((function(e){return e.highlighted}));((t={})[d.TEXT_TYPE]=function(){n===i.input.element&&(i.containerOuter.removeFocusState(),r&&i.unhighlightAll(),i.hideDropdown(!0))},t[d.SELECT_ONE_TYPE]=function(){i.containerOuter.removeFocusState(),(n===i.input.element||n===i.containerOuter.element&&!i._canSearch)&&i.hideDropdown(!0)},t[d.SELECT_MULTIPLE_TYPE]=function(){n===i.input.element&&(i.containerOuter.removeFocusState(),i.hideDropdown(!0),r&&i.unhighlightAll())},t)[this.passedElement.element.type]()}else this._isScrollingOnIe=!1,this.input.element.focus()},e.prototype._onFormReset=function(){this._store.dispatch((0,h.resetTo)(this._initialState))},e.prototype._highlightChoice=function(e){var t=this;void 0===e&&(e=null);var i=Array.from(this.dropdown.element.querySelectorAll("[data-choice-selectable]"));if(i.length){var n=e;Array.from(this.dropdown.element.querySelectorAll(".".concat(this.config.classNames.highlightedState))).forEach((function(e){e.classList.remove(t.config.classNames.highlightedState),e.setAttribute("aria-selected","false")})),n?this._highlightPosition=i.indexOf(n):(n=i.length>this._highlightPosition?i[this._highlightPosition]:i[i.length-1])||(n=i[0]),n.classList.add(this.config.classNames.highlightedState),n.setAttribute("aria-selected","true"),this.passedElement.triggerEvent(d.EVENTS.highlightChoice,{el:n}),this.dropdown.isActive&&(this.input.setActiveDescendant(n.id),this.containerOuter.setActiveDescendant(n.id))}},e.prototype._addItem=function(e){var t=e.value,i=e.label,n=void 0===i?null:i,r=e.choiceId,s=void 0===r?-1:r,o=e.groupId,a=void 0===o?-1:o,c=e.customProperties,h=void 0===c?{}:c,u=e.placeholder,p=void 0!==u&&u,f=e.keyCode,m=void 0===f?-1:f,v="string"==typeof t?t.trim():t,g=this._store.items,_=n||v,y=s||-1,E=a>=0?this._store.getGroupById(a):null,b=g?g.length+1:1;this.config.prependValue&&(v=this.config.prependValue+v.toString()),this.config.appendValue&&(v+=this.config.appendValue.toString()),this._store.dispatch((0,l.addItem)({value:v,label:_,id:b,choiceId:y,groupId:a,customProperties:h,placeholder:p,keyCode:m})),this._isSelectOneElement&&this.removeActiveItems(b),this.passedElement.triggerEvent(d.EVENTS.addItem,{id:b,value:v,label:_,customProperties:h,groupValue:E&&E.value?E.value:null,keyCode:m})},e.prototype._removeItem=function(e){var t=e.id,i=e.value,n=e.label,r=e.customProperties,s=e.choiceId,o=e.groupId,a=o&&o>=0?this._store.getGroupById(o):null;t&&s&&(this._store.dispatch((0,l.removeItem)(t,s)),this.passedElement.triggerEvent(d.EVENTS.removeItem,{id:t,value:i,label:n,customProperties:r,groupValue:a&&a.value?a.value:null}))},e.prototype._addChoice=function(e){var t=e.value,i=e.label,n=void 0===i?null:i,r=e.isSelected,s=void 0!==r&&r,o=e.isDisabled,c=void 0!==o&&o,l=e.groupId,h=void 0===l?-1:l,u=e.customProperties,d=void 0===u?{}:u,p=e.placeholder,f=void 0!==p&&p,m=e.keyCode,v=void 0===m?-1:m;if(null!=t){var g=this._store.choices,_=n||t,y=g?g.length+1:1,E="".concat(this._baseId,"-").concat(this._idNames.itemChoice,"-").concat(y);this._store.dispatch((0,a.addChoice)({id:y,groupId:h,elementId:E,value:t,label:_,disabled:c,customProperties:d,placeholder:f,keyCode:v})),s&&this._addItem({value:t,label:_,choiceId:y,customProperties:d,placeholder:f,keyCode:v})}},e.prototype._addGroup=function(e){var t=this,i=e.group,n=e.id,r=e.valueKey,s=void 0===r?"value":r,o=e.labelKey,a=void 0===o?"label":o,l=(0,f.isType)("Object",i)?i.choices:Array.from(i.getElementsByTagName("OPTION")),h=n||Math.floor((new Date).valueOf()*Math.random()),u=!!i.disabled&&i.disabled;l?(this._store.dispatch((0,c.addGroup)({value:i.label,id:h,active:!0,disabled:u})),l.forEach((function(e){var i=e.disabled||e.parentNode&&e.parentNode.disabled;t._addChoice({value:e[s],label:(0,f.isType)("Object",e)?e[a]:e.innerHTML,isSelected:e.selected,isDisabled:i,groupId:h,customProperties:e.customProperties,placeholder:e.placeholder})}))):this._store.dispatch((0,c.addGroup)({value:i.label,id:i.id,active:!1,disabled:i.disabled}))},e.prototype._getTemplate=function(e){for(var t,i=[],r=1;r<arguments.length;r++)i[r-1]=arguments[r];return(t=this._templates[e]).call.apply(t,n([this,this.config],i,!1))},e.prototype._createTemplates=function(){var e=this.config.callbackOnCreateTemplates,t={};e&&"function"==typeof e&&(t=e.call(this,f.strToEl)),this._templates=(0,s.default)(g.default,t)},e.prototype._createElements=function(){this.containerOuter=new u.Container({element:this._getTemplate("containerOuter",this._direction,this._isSelectElement,this._isSelectOneElement,this.config.searchEnabled,this.passedElement.element.type,this.config.labelId),classNames:this.config.classNames,type:this.passedElement.element.type,position:this.config.position}),this.containerInner=new u.Container({element:this._getTemplate("containerInner"),classNames:this.config.classNames,type:this.passedElement.element.type,position:this.config.position}),this.input=new u.Input({element:this._getTemplate("input",this._placeholderValue),classNames:this.config.classNames,type:this.passedElement.element.type,preventPaste:!this.config.paste}),this.choiceList=new u.List({element:this._getTemplate("choiceList",this._isSelectOneElement)}),this.itemList=new u.List({element:this._getTemplate("itemList",this._isSelectOneElement)}),this.dropdown=new u.Dropdown({element:this._getTemplate("dropdown"),classNames:this.config.classNames,type:this.passedElement.element.type})},e.prototype._createStructure=function(){this.passedElement.conceal(),this.containerInner.wrap(this.passedElement.element),this.containerOuter.wrap(this.containerInner.element),this._isSelectOneElement?this.input.placeholder=this.config.searchPlaceholderValue||"":this._placeholderValue&&(this.input.placeholder=this._placeholderValue,this.input.setWidth()),this.containerOuter.element.appendChild(this.containerInner.element),this.containerOuter.element.appendChild(this.dropdown.element),this.containerInner.element.appendChild(this.itemList.element),this._isTextElement||this.dropdown.element.appendChild(this.choiceList.element),this._isSelectOneElement?this.config.searchEnabled&&this.dropdown.element.insertBefore(this.input.element,this.dropdown.element.firstChild):this.containerInner.element.appendChild(this.input.element),this._isSelectElement&&(this._highlightPosition=0,this._isSearching=!1,this._startLoading(),this._presetGroups.length?this._addPredefinedGroups(this._presetGroups):this._addPredefinedChoices(this._presetChoices),this._stopLoading()),this._isTextElement&&this._addPredefinedItems(this._presetItems)},e.prototype._addPredefinedGroups=function(e){var t=this,i=this.passedElement.placeholderOption;i&&i.parentNode&&"SELECT"===i.parentNode.tagName&&this._addChoice({value:i.value,label:i.innerHTML,isSelected:i.selected,isDisabled:i.disabled,placeholder:!0}),e.forEach((function(e){return t._addGroup({group:e,id:e.id||null})}))},e.prototype._addPredefinedChoices=function(e){var t=this;this.config.shouldSort&&e.sort(this.config.sorter);var i=e.some((function(e){return e.selected})),n=e.findIndex((function(e){return void 0===e.disabled||!e.disabled}));e.forEach((function(e,r){var s=e.value,o=void 0===s?"":s,a=e.label,c=e.customProperties,l=e.placeholder;if(t._isSelectElement)if(e.choices)t._addGroup({group:e,id:e.id||null});else{var h=!(!t._isSelectOneElement||i||r!==n)||e.selected,u=e.disabled;t._addChoice({value:o,label:a,isSelected:!!h,isDisabled:!!u,placeholder:!!l,customProperties:c})}else t._addChoice({value:o,label:a,isSelected:!!e.selected,isDisabled:!!e.disabled,placeholder:!!e.placeholder,customProperties:c})}))},e.prototype._addPredefinedItems=function(e){var t=this;e.forEach((function(e){"object"==typeof e&&e.value&&t._addItem({value:e.value,label:e.label,choiceId:e.id,customProperties:e.customProperties,placeholder:e.placeholder}),"string"==typeof e&&t._addItem({value:e})}))},e.prototype._setChoiceOrItem=function(e){var t=this;({object:function(){e.value&&(t._isTextElement?t._addItem({value:e.value,label:e.label,choiceId:e.id,customProperties:e.customProperties,placeholder:e.placeholder}):t._addChoice({value:e.value,label:e.label,isSelected:!0,isDisabled:!1,customProperties:e.customProperties,placeholder:e.placeholder}))},string:function(){t._isTextElement?t._addItem({value:e}):t._addChoice({value:e,label:e,isSelected:!0,isDisabled:!1})}})[(0,f.getType)(e).toLowerCase()]()},e.prototype._findAndSelectChoiceByValue=function(e){var t=this,i=this._store.choices.find((function(i){return t.config.valueComparer(i.value,e)}));i&&!i.selected&&this._addItem({value:i.value,label:i.label,choiceId:i.id,groupId:i.groupId,customProperties:i.customProperties,placeholder:i.placeholder,keyCode:i.keyCode})},e.prototype._generatePlaceholderValue=function(){if(this._isSelectElement&&this.passedElement.placeholderOption){var e=this.passedElement.placeholderOption;return e?e.text:null}var t=this.config,i=t.placeholder,n=t.placeholderValue,r=this.passedElement.element.dataset;if(i){if(n)return n;if(r.placeholder)return r.placeholder}return null},e}();t.default=E},613:function(e,t,i){Object.defineProperty(t,"__esModule",{value:!0});var n=i(799),r=i(883),s=function(){function e(e){var t=e.element,i=e.type,n=e.classNames,r=e.position;this.element=t,this.classNames=n,this.type=i,this.position=r,this.isOpen=!1,this.isFlipped=!1,this.isFocussed=!1,this.isDisabled=!1,this.isLoading=!1,this._onFocus=this._onFocus.bind(this),this._onBlur=this._onBlur.bind(this)}return e.prototype.addEventListeners=function(){this.element.addEventListener("focus",this._onFocus),this.element.addEventListener("blur",this._onBlur)},e.prototype.removeEventListeners=function(){this.element.removeEventListener("focus",this._onFocus),this.element.removeEventListener("blur",this._onBlur)},e.prototype.shouldFlip=function(e){if("number"!=typeof e)return!1;var t=!1;return"auto"===this.position?t=!window.matchMedia("(min-height: ".concat(e+1,"px)")).matches:"top"===this.position&&(t=!0),t},e.prototype.setActiveDescendant=function(e){this.element.setAttribute("aria-activedescendant",e)},e.prototype.removeActiveDescendant=function(){this.element.removeAttribute("aria-activedescendant")},e.prototype.open=function(e){this.element.classList.add(this.classNames.openState),this.element.setAttribute("aria-expanded","true"),this.isOpen=!0,this.shouldFlip(e)&&(this.element.classList.add(this.classNames.flippedState),this.isFlipped=!0)},e.prototype.close=function(){this.element.classList.remove(this.classNames.openState),this.element.setAttribute("aria-expanded","false"),this.removeActiveDescendant(),this.isOpen=!1,this.isFlipped&&(this.element.classList.remove(this.classNames.flippedState),this.isFlipped=!1)},e.prototype.focus=function(){this.isFocussed||this.element.focus()},e.prototype.addFocusState=function(){this.element.classList.add(this.classNames.focusState)},e.prototype.removeFocusState=function(){this.element.classList.remove(this.classNames.focusState)},e.prototype.enable=function(){this.element.classList.remove(this.classNames.disabledState),this.element.removeAttribute("aria-disabled"),this.type===r.SELECT_ONE_TYPE&&this.element.setAttribute("tabindex","0"),this.isDisabled=!1},e.prototype.disable=function(){this.element.classList.add(this.classNames.disabledState),this.element.setAttribute("aria-disabled","true"),this.type===r.SELECT_ONE_TYPE&&this.element.setAttribute("tabindex","-1"),this.isDisabled=!0},e.prototype.wrap=function(e){(0,n.wrap)(e,this.element)},e.prototype.unwrap=function(e){this.element.parentNode&&(this.element.parentNode.insertBefore(e,this.element),this.element.parentNode.removeChild(this.element))},e.prototype.addLoadingState=function(){this.element.classList.add(this.classNames.loadingState),this.element.setAttribute("aria-busy","true"),this.isLoading=!0},e.prototype.removeLoadingState=function(){this.element.classList.remove(this.classNames.loadingState),this.element.removeAttribute("aria-busy"),this.isLoading=!1},e.prototype._onFocus=function(){this.isFocussed=!0},e.prototype._onBlur=function(){this.isFocussed=!1},e}();t.default=s},217:function(e,t){Object.defineProperty(t,"__esModule",{value:!0});var i=function(){function e(e){var t=e.element,i=e.type,n=e.classNames;this.element=t,this.classNames=n,this.type=i,this.isActive=!1}return Object.defineProperty(e.prototype,"distanceFromTopWindow",{get:function(){return this.element.getBoundingClientRect().bottom},enumerable:!1,configurable:!0}),e.prototype.getChild=function(e){return this.element.querySelector(e)},e.prototype.show=function(){return this.element.classList.add(this.classNames.activeState),this.element.setAttribute("aria-expanded","true"),this.isActive=!0,this},e.prototype.hide=function(){return this.element.classList.remove(this.classNames.activeState),this.element.setAttribute("aria-expanded","false"),this.isActive=!1,this},e}();t.default=i},520:function(e,t,i){var n=this&&this.__importDefault||function(e){return e&&e.__esModule?e:{default:e}};Object.defineProperty(t,"__esModule",{value:!0}),t.WrappedSelect=t.WrappedInput=t.List=t.Input=t.Container=t.Dropdown=void 0;var r=n(i(217));t.Dropdown=r.default;var s=n(i(613));t.Container=s.default;var o=n(i(11));t.Input=o.default;var a=n(i(624));t.List=a.default;var c=n(i(541));t.WrappedInput=c.default;var l=n(i(982));t.WrappedSelect=l.default},11:function(e,t,i){Object.defineProperty(t,"__esModule",{value:!0});var n=i(799),r=i(883),s=function(){function e(e){var t=e.element,i=e.type,n=e.classNames,r=e.preventPaste;this.element=t,this.type=i,this.classNames=n,this.preventPaste=r,this.isFocussed=this.element.isEqualNode(document.activeElement),this.isDisabled=t.disabled,this._onPaste=this._onPaste.bind(this),this._onInput=this._onInput.bind(this),this._onFocus=this._onFocus.bind(this),this._onBlur=this._onBlur.bind(this)}return Object.defineProperty(e.prototype,"placeholder",{set:function(e){this.element.placeholder=e},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"value",{get:function(){return(0,n.sanitise)(this.element.value)},set:function(e){this.element.value=e},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"rawValue",{get:function(){return this.element.value},enumerable:!1,configurable:!0}),e.prototype.addEventListeners=function(){this.element.addEventListener("paste",this._onPaste),this.element.addEventListener("input",this._onInput,{passive:!0}),this.element.addEventListener("focus",this._onFocus,{passive:!0}),this.element.addEventListener("blur",this._onBlur,{passive:!0})},e.prototype.removeEventListeners=function(){this.element.removeEventListener("input",this._onInput),this.element.removeEventListener("paste",this._onPaste),this.element.removeEventListener("focus",this._onFocus),this.element.removeEventListener("blur",this._onBlur)},e.prototype.enable=function(){this.element.removeAttribute("disabled"),this.isDisabled=!1},e.prototype.disable=function(){this.element.setAttribute("disabled",""),this.isDisabled=!0},e.prototype.focus=function(){this.isFocussed||this.element.focus()},e.prototype.blur=function(){this.isFocussed&&this.element.blur()},e.prototype.clear=function(e){return void 0===e&&(e=!0),this.element.value&&(this.element.value=""),e&&this.setWidth(),this},e.prototype.setWidth=function(){var e=this.element,t=e.style,i=e.value,n=e.placeholder;t.minWidth="".concat(n.length+1,"ch"),t.width="".concat(i.length+1,"ch")},e.prototype.setActiveDescendant=function(e){this.element.setAttribute("aria-activedescendant",e)},e.prototype.removeActiveDescendant=function(){this.element.removeAttribute("aria-activedescendant")},e.prototype._onInput=function(){this.type!==r.SELECT_ONE_TYPE&&this.setWidth()},e.prototype._onPaste=function(e){this.preventPaste&&e.preventDefault()},e.prototype._onFocus=function(){this.isFocussed=!0},e.prototype._onBlur=function(){this.isFocussed=!1},e}();t.default=s},624:function(e,t,i){Object.defineProperty(t,"__esModule",{value:!0});var n=i(883),r=function(){function e(e){var t=e.element;this.element=t,this.scrollPos=this.element.scrollTop,this.height=this.element.offsetHeight}return e.prototype.clear=function(){this.element.innerHTML=""},e.prototype.append=function(e){this.element.appendChild(e)},e.prototype.getChild=function(e){return this.element.querySelector(e)},e.prototype.hasChildren=function(){return this.element.hasChildNodes()},e.prototype.scrollToTop=function(){this.element.scrollTop=0},e.prototype.scrollToChildElement=function(e,t){var i=this;if(e){var n=this.element.offsetHeight,r=this.element.scrollTop+n,s=e.offsetHeight,o=e.offsetTop+s,a=t>0?this.element.scrollTop+o-r:e.offsetTop;requestAnimationFrame((function(){i._animateScroll(a,t)}))}},e.prototype._scrollDown=function(e,t,i){var n=(i-e)/t,r=n>1?n:1;this.element.scrollTop=e+r},e.prototype._scrollUp=function(e,t,i){var n=(e-i)/t,r=n>1?n:1;this.element.scrollTop=e-r},e.prototype._animateScroll=function(e,t){var i=this,r=n.SCROLLING_SPEED,s=this.element.scrollTop,o=!1;t>0?(this._scrollDown(s,r,e),s<e&&(o=!0)):(this._scrollUp(s,r,e),s>e&&(o=!0)),o&&requestAnimationFrame((function(){i._animateScroll(e,t)}))},e}();t.default=r},730:function(e,t,i){Object.defineProperty(t,"__esModule",{value:!0});var n=i(799),r=function(){function e(e){var t=e.element,i=e.classNames;if(this.element=t,this.classNames=i,!(t instanceof HTMLInputElement||t instanceof HTMLSelectElement))throw new TypeError("Invalid element passed");this.isDisabled=!1}return Object.defineProperty(e.prototype,"isActive",{get:function(){return"active"===this.element.dataset.choice},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"dir",{get:function(){return this.element.dir},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"value",{get:function(){return this.element.value},set:function(e){this.element.value=e},enumerable:!1,configurable:!0}),e.prototype.conceal=function(){this.element.classList.add(this.classNames.input),this.element.hidden=!0,this.element.tabIndex=-1;var e=this.element.getAttribute("style");e&&this.element.setAttribute("data-choice-orig-style",e),this.element.setAttribute("data-choice","active")},e.prototype.reveal=function(){this.element.classList.remove(this.classNames.input),this.element.hidden=!1,this.element.removeAttribute("tabindex");var e=this.element.getAttribute("data-choice-orig-style");e?(this.element.removeAttribute("data-choice-orig-style"),this.element.setAttribute("style",e)):this.element.removeAttribute("style"),this.element.removeAttribute("data-choice"),this.element.value=this.element.value},e.prototype.enable=function(){this.element.removeAttribute("disabled"),this.element.disabled=!1,this.isDisabled=!1},e.prototype.disable=function(){this.element.setAttribute("disabled",""),this.element.disabled=!0,this.isDisabled=!0},e.prototype.triggerEvent=function(e,t){(0,n.dispatchEvent)(this.element,e,t)},e}();t.default=r},541:function(e,t,i){var n,r=this&&this.__extends||(n=function(e,t){return n=Object.setPrototypeOf||{__proto__:[]}instanceof Array&&function(e,t){e.__proto__=t}||function(e,t){for(var i in t)Object.prototype.hasOwnProperty.call(t,i)&&(e[i]=t[i])},n(e,t)},function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Class extends value "+String(t)+" is not a constructor or null");function i(){this.constructor=e}n(e,t),e.prototype=null===t?Object.create(t):(i.prototype=t.prototype,new i)}),s=this&&this.__importDefault||function(e){return e&&e.__esModule?e:{default:e}};Object.defineProperty(t,"__esModule",{value:!0});var o=function(e){function t(t){var i=t.element,n=t.classNames,r=t.delimiter,s=e.call(this,{element:i,classNames:n})||this;return s.delimiter=r,s}return r(t,e),Object.defineProperty(t.prototype,"value",{get:function(){return this.element.value},set:function(e){this.element.setAttribute("value",e),this.element.value=e},enumerable:!1,configurable:!0}),t}(s(i(730)).default);t.default=o},982:function(e,t,i){var n,r=this&&this.__extends||(n=function(e,t){return n=Object.setPrototypeOf||{__proto__:[]}instanceof Array&&function(e,t){e.__proto__=t}||function(e,t){for(var i in t)Object.prototype.hasOwnProperty.call(t,i)&&(e[i]=t[i])},n(e,t)},function(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Class extends value "+String(t)+" is not a constructor or null");function i(){this.constructor=e}n(e,t),e.prototype=null===t?Object.create(t):(i.prototype=t.prototype,new i)}),s=this&&this.__importDefault||function(e){return e&&e.__esModule?e:{default:e}};Object.defineProperty(t,"__esModule",{value:!0});var o=function(e){function t(t){var i=t.element,n=t.classNames,r=t.template,s=e.call(this,{element:i,classNames:n})||this;return s.template=r,s}return r(t,e),Object.defineProperty(t.prototype,"placeholderOption",{get:function(){return this.element.querySelector('option[value=""]')||this.element.querySelector("option[placeholder]")},enumerable:!1,configurable:!0}),Object.defineProperty(t.prototype,"optionGroups",{get:function(){return Array.from(this.element.getElementsByTagName("OPTGROUP"))},enumerable:!1,configurable:!0}),Object.defineProperty(t.prototype,"options",{get:function(){return Array.from(this.element.options)},set:function(e){var t=this,i=document.createDocumentFragment();e.forEach((function(e){return n=e,r=t.template(n),void i.appendChild(r);var n,r})),this.appendDocFragment(i)},enumerable:!1,configurable:!0}),t.prototype.appendDocFragment=function(e){this.element.innerHTML="",this.element.appendChild(e)},t}(s(i(730)).default);t.default=o},883:function(e,t){Object.defineProperty(t,"__esModule",{value:!0}),t.SCROLLING_SPEED=t.SELECT_MULTIPLE_TYPE=t.SELECT_ONE_TYPE=t.TEXT_TYPE=t.KEY_CODES=t.ACTION_TYPES=t.EVENTS=void 0,t.EVENTS={showDropdown:"showDropdown",hideDropdown:"hideDropdown",change:"change",choice:"choice",search:"search",addItem:"addItem",removeItem:"removeItem",highlightItem:"highlightItem",highlightChoice:"highlightChoice",unhighlightItem:"unhighlightItem"},t.ACTION_TYPES={ADD_CHOICE:"ADD_CHOICE",FILTER_CHOICES:"FILTER_CHOICES",ACTIVATE_CHOICES:"ACTIVATE_CHOICES",CLEAR_CHOICES:"CLEAR_CHOICES",ADD_GROUP:"ADD_GROUP",ADD_ITEM:"ADD_ITEM",REMOVE_ITEM:"REMOVE_ITEM",HIGHLIGHT_ITEM:"HIGHLIGHT_ITEM",CLEAR_ALL:"CLEAR_ALL",RESET_TO:"RESET_TO",SET_IS_LOADING:"SET_IS_LOADING"},t.KEY_CODES={BACK_KEY:46,DELETE_KEY:8,ENTER_KEY:13,A_KEY:65,ESC_KEY:27,UP_KEY:38,DOWN_KEY:40,PAGE_UP_KEY:33,PAGE_DOWN_KEY:34},t.TEXT_TYPE="text",t.SELECT_ONE_TYPE="select-one",t.SELECT_MULTIPLE_TYPE="select-multiple",t.SCROLLING_SPEED=4},789:function(e,t,i){Object.defineProperty(t,"__esModule",{value:!0}),t.DEFAULT_CONFIG=t.DEFAULT_CLASSNAMES=void 0;var n=i(799);t.DEFAULT_CLASSNAMES={containerOuter:"choices",containerInner:"choices__inner",input:"choices__input",inputCloned:"choices__input--cloned",list:"choices__list",listItems:"choices__list--multiple",listSingle:"choices__list--single",listDropdown:"choices__list--dropdown",item:"choices__item",itemSelectable:"choices__item--selectable",itemDisabled:"choices__item--disabled",itemChoice:"choices__item--choice",placeholder:"choices__placeholder",group:"choices__group",groupHeading:"choices__heading",button:"choices__button",activeState:"is-active",focusState:"is-focused",openState:"is-open",disabledState:"is-disabled",highlightedState:"is-highlighted",selectedState:"is-selected",flippedState:"is-flipped",loadingState:"is-loading",noResults:"has-no-results",noChoices:"has-no-choices"},t.DEFAULT_CONFIG={items:[],choices:[],silent:!1,renderChoiceLimit:-1,maxItemCount:-1,addItems:!0,addItemFilter:null,removeItems:!0,removeItemButton:!1,editItems:!1,allowHTML:!0,duplicateItemsAllowed:!0,delimiter:",",paste:!0,searchEnabled:!0,searchChoices:!0,searchFloor:1,searchResultLimit:4,searchFields:["label","value"],position:"auto",resetScrollPosition:!0,shouldSort:!0,shouldSortItems:!1,sorter:n.sortByAlpha,placeholder:!0,placeholderValue:null,searchPlaceholderValue:null,prependValue:null,appendValue:null,renderSelectedChoices:"auto",loadingText:"Loading...",noResultsText:"No results found",noChoicesText:"No choices to choose from",itemSelectText:"Press to select",uniqueItemText:"Only unique values can be added",customAddItemText:"Only values matching specific conditions can be added",addItemText:function(e){return'Press Enter to add <b>"'.concat((0,n.sanitise)(e),'"</b>')},maxItemText:function(e){return"Only ".concat(e," values can be added")},valueComparer:function(e,t){return e===t},fuseOptions:{includeScore:!0},labelId:"",callbackOnInit:null,callbackOnCreateTemplates:null,classNames:t.DEFAULT_CLASSNAMES}},18:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},978:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},948:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},359:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},285:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},533:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},187:function(e,t,i){var n=this&&this.__createBinding||(Object.create?function(e,t,i,n){void 0===n&&(n=i);var r=Object.getOwnPropertyDescriptor(t,i);r&&!("get"in r?!t.__esModule:r.writable||r.configurable)||(r={enumerable:!0,get:function(){return t[i]}}),Object.defineProperty(e,n,r)}:function(e,t,i,n){void 0===n&&(n=i),e[n]=t[i]}),r=this&&this.__exportStar||function(e,t){for(var i in e)"default"===i||Object.prototype.hasOwnProperty.call(t,i)||n(t,e,i)};Object.defineProperty(t,"__esModule",{value:!0}),r(i(18),t),r(i(978),t),r(i(948),t),r(i(359),t),r(i(285),t),r(i(533),t),r(i(287),t),r(i(132),t),r(i(837),t),r(i(598),t),r(i(369),t),r(i(37),t),r(i(47),t),r(i(923),t),r(i(876),t)},287:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},132:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},837:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},598:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},37:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},369:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},47:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},923:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},876:function(e,t){Object.defineProperty(t,"__esModule",{value:!0})},799:function(e,t){var i;Object.defineProperty(t,"__esModule",{value:!0}),t.parseCustomProperties=t.diff=t.cloneObject=t.existsInArray=t.dispatchEvent=t.sortByScore=t.sortByAlpha=t.strToEl=t.sanitise=t.isScrolledIntoView=t.getAdjacentEl=t.wrap=t.isType=t.getType=t.generateId=t.generateChars=t.getRandomNumber=void 0,t.getRandomNumber=function(e,t){return Math.floor(Math.random()*(t-e)+e)},t.generateChars=function(e){return Array.from({length:e},(function(){return(0,t.getRandomNumber)(0,36).toString(36)})).join("")},t.generateId=function(e,i){var n=e.id||e.name&&"".concat(e.name,"-").concat((0,t.generateChars)(2))||(0,t.generateChars)(4);return n=n.replace(/(:|\.|\[|\]|,)/g,""),"".concat(i,"-").concat(n)},t.getType=function(e){return Object.prototype.toString.call(e).slice(8,-1)},t.isType=function(e,i){return null!=i&&(0,t.getType)(i)===e},t.wrap=function(e,t){return void 0===t&&(t=document.createElement("div")),e.parentNode&&(e.nextSibling?e.parentNode.insertBefore(t,e.nextSibling):e.parentNode.appendChild(t)),t.appendChild(e)},t.getAdjacentEl=function(e,t,i){void 0===i&&(i=1);for(var n="".concat(i>0?"next":"previous","ElementSibling"),r=e[n];r;){if(r.matches(t))return r;r=r[n]}return r},t.isScrolledIntoView=function(e,t,i){return void 0===i&&(i=1),!!e&&(i>0?t.scrollTop+t.offsetHeight>=e.offsetTop+e.offsetHeight:e.offsetTop>=t.scrollTop)},t.sanitise=function(e){return"string"!=typeof e?e:e.replace(/&/g,"&amp;").replace(/>/g,"&gt;").replace(/</g,"&lt;").replace(/"/g,"&quot;")},t.strToEl=(i=document.createElement("div"),function(e){var t=e.trim();i.innerHTML=t;for(var n=i.children[0];i.firstChild;)i.removeChild(i.firstChild);return n}),t.sortByAlpha=function(e,t){var i=e.value,n=e.label,r=void 0===n?i:n,s=t.value,o=t.label,a=void 0===o?s:o;return r.localeCompare(a,[],{sensitivity:"base",ignorePunctuation:!0,numeric:!0})},t.sortByScore=function(e,t){var i=e.score,n=void 0===i?0:i,r=t.score;return n-(void 0===r?0:r)},t.dispatchEvent=function(e,t,i){void 0===i&&(i=null);var n=new CustomEvent(t,{detail:i,bubbles:!0,cancelable:!0});return e.dispatchEvent(n)},t.existsInArray=function(e,t,i){return void 0===i&&(i="value"),e.some((function(e){return"string"==typeof t?e[i]===t.trim():e[i]===t}))},t.cloneObject=function(e){return JSON.parse(JSON.stringify(e))},t.diff=function(e,t){var i=Object.keys(e).sort(),n=Object.keys(t).sort();return i.filter((function(e){return n.indexOf(e)<0}))},t.parseCustomProperties=function(e){if(void 0!==e)try{return JSON.parse(e)}catch(t){return e}return{}}},273:function(e,t){var i=this&&this.__spreadArray||function(e,t,i){if(i||2===arguments.length)for(var n,r=0,s=t.length;r<s;r++)!n&&r in t||(n||(n=Array.prototype.slice.call(t,0,r)),n[r]=t[r]);return e.concat(n||Array.prototype.slice.call(t))};Object.defineProperty(t,"__esModule",{value:!0}),t.defaultState=void 0,t.defaultState=[],t.default=function(e,n){switch(void 0===e&&(e=t.defaultState),void 0===n&&(n={}),n.type){case"ADD_CHOICE":var r=n,s={id:r.id,elementId:r.elementId,groupId:r.groupId,value:r.value,label:r.label||r.value,disabled:r.disabled||!1,selected:!1,active:!0,score:9999,customProperties:r.customProperties,placeholder:r.placeholder||!1};return i(i([],e,!0),[s],!1);case"ADD_ITEM":var o=n;return o.choiceId>-1?e.map((function(e){var t=e;return t.id===parseInt("".concat(o.choiceId),10)&&(t.selected=!0),t})):e;case"REMOVE_ITEM":var a=n;return a.choiceId&&a.choiceId>-1?e.map((function(e){var t=e;return t.id===parseInt("".concat(a.choiceId),10)&&(t.selected=!1),t})):e;case"FILTER_CHOICES":var c=n;return e.map((function(e){var t=e;return t.active=c.results.some((function(e){var i=e.item,n=e.score;return i.id===t.id&&(t.score=n,!0)})),t}));case"ACTIVATE_CHOICES":var l=n;return e.map((function(e){var t=e;return t.active=l.active,t}));case"CLEAR_CHOICES":return t.defaultState;default:return e}}},871:function(e,t){var i=this&&this.__spreadArray||function(e,t,i){if(i||2===arguments.length)for(var n,r=0,s=t.length;r<s;r++)!n&&r in t||(n||(n=Array.prototype.slice.call(t,0,r)),n[r]=t[r]);return e.concat(n||Array.prototype.slice.call(t))};Object.defineProperty(t,"__esModule",{value:!0}),t.defaultState=void 0,t.defaultState=[],t.default=function(e,n){switch(void 0===e&&(e=t.defaultState),void 0===n&&(n={}),n.type){case"ADD_GROUP":var r=n;return i(i([],e,!0),[{id:r.id,value:r.value,active:r.active,disabled:r.disabled}],!1);case"CLEAR_CHOICES":return[];default:return e}}},655:function(e,t,i){var n=this&&this.__importDefault||function(e){return e&&e.__esModule?e:{default:e}};Object.defineProperty(t,"__esModule",{value:!0}),t.defaultState=void 0;var r=i(791),s=n(i(52)),o=n(i(871)),a=n(i(273)),c=n(i(502)),l=i(799);t.defaultState={groups:[],items:[],choices:[],loading:!1};var h=(0,r.combineReducers)({items:s.default,groups:o.default,choices:a.default,loading:c.default});t.default=function(e,i){var n=e;if("CLEAR_ALL"===i.type)n=t.defaultState;else if("RESET_TO"===i.type)return(0,l.cloneObject)(i.state);return h(n,i)}},52:function(e,t){var i=this&&this.__spreadArray||function(e,t,i){if(i||2===arguments.length)for(var n,r=0,s=t.length;r<s;r++)!n&&r in t||(n||(n=Array.prototype.slice.call(t,0,r)),n[r]=t[r]);return e.concat(n||Array.prototype.slice.call(t))};Object.defineProperty(t,"__esModule",{value:!0}),t.defaultState=void 0,t.defaultState=[],t.default=function(e,n){switch(void 0===e&&(e=t.defaultState),void 0===n&&(n={}),n.type){case"ADD_ITEM":var r=n;return i(i([],e,!0),[{id:r.id,choiceId:r.choiceId,groupId:r.groupId,value:r.value,label:r.label,active:!0,highlighted:!1,customProperties:r.customProperties,placeholder:r.placeholder||!1,keyCode:null}],!1).map((function(e){var t=e;return t.highlighted=!1,t}));case"REMOVE_ITEM":return e.map((function(e){var t=e;return t.id===n.id&&(t.active=!1),t}));case"HIGHLIGHT_ITEM":var s=n;return e.map((function(e){var t=e;return t.id===s.id&&(t.highlighted=s.highlighted),t}));default:return e}}},502:function(e,t){Object.defineProperty(t,"__esModule",{value:!0}),t.defaultState=void 0,t.defaultState=!1,t.default=function(e,i){return void 0===e&&(e=t.defaultState),void 0===i&&(i={}),"SET_IS_LOADING"===i.type?i.isLoading:e}},744:function(e,t,i){var n=this&&this.__spreadArray||function(e,t,i){if(i||2===arguments.length)for(var n,r=0,s=t.length;r<s;r++)!n&&r in t||(n||(n=Array.prototype.slice.call(t,0,r)),n[r]=t[r]);return e.concat(n||Array.prototype.slice.call(t))},r=this&&this.__importDefault||function(e){return e&&e.__esModule?e:{default:e}};Object.defineProperty(t,"__esModule",{value:!0});var s=i(791),o=r(i(655)),a=function(){function e(){this._store=(0,s.createStore)(o.default,window.__REDUX_DEVTOOLS_EXTENSION__&&window.__REDUX_DEVTOOLS_EXTENSION__())}return e.prototype.subscribe=function(e){this._store.subscribe(e)},e.prototype.dispatch=function(e){this._store.dispatch(e)},Object.defineProperty(e.prototype,"state",{get:function(){return this._store.getState()},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"items",{get:function(){return this.state.items},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"activeItems",{get:function(){return this.items.filter((function(e){return!0===e.active}))},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"highlightedActiveItems",{get:function(){return this.items.filter((function(e){return e.active&&e.highlighted}))},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"choices",{get:function(){return this.state.choices},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"activeChoices",{get:function(){return this.choices.filter((function(e){return!0===e.active}))},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"selectableChoices",{get:function(){return this.choices.filter((function(e){return!0!==e.disabled}))},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"searchableChoices",{get:function(){return this.selectableChoices.filter((function(e){return!0!==e.placeholder}))},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"placeholderChoice",{get:function(){return n([],this.choices,!0).reverse().find((function(e){return!0===e.placeholder}))},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"groups",{get:function(){return this.state.groups},enumerable:!1,configurable:!0}),Object.defineProperty(e.prototype,"activeGroups",{get:function(){var e=this.groups,t=this.choices;return e.filter((function(e){var i=!0===e.active&&!1===e.disabled,n=t.some((function(e){return!0===e.active&&!1===e.disabled}));return i&&n}),[])},enumerable:!1,configurable:!0}),e.prototype.isLoading=function(){return this.state.loading},e.prototype.getChoiceById=function(e){return this.activeChoices.find((function(t){return t.id===parseInt(e,10)}))},e.prototype.getGroupById=function(e){return this.groups.find((function(t){return t.id===e}))},e}();t.default=a},686:function(e,t){Object.defineProperty(t,"__esModule",{value:!0});var i={containerOuter:function(e,t,i,n,r,s,o){var a=e.classNames.containerOuter,c=Object.assign(document.createElement("div"),{className:a});return c.dataset.type=s,t&&(c.dir=t),n&&(c.tabIndex=0),i&&(c.setAttribute("role",r?"combobox":"listbox"),r&&c.setAttribute("aria-autocomplete","list")),c.setAttribute("aria-haspopup","true"),c.setAttribute("aria-expanded","false"),o&&c.setAttribute("aria-labelledby",o),c},containerInner:function(e){var t=e.classNames.containerInner;return Object.assign(document.createElement("div"),{className:t})},itemList:function(e,t){var i=e.classNames,n=i.list,r=i.listSingle,s=i.listItems;return Object.assign(document.createElement("div"),{className:"".concat(n," ").concat(t?r:s)})},placeholder:function(e,t){var i,n=e.allowHTML,r=e.classNames.placeholder;return Object.assign(document.createElement("div"),((i={className:r})[n?"innerHTML":"innerText"]=t,i))},item:function(e,t,i){var n,r,s=e.allowHTML,o=e.classNames,a=o.item,c=o.button,l=o.highlightedState,h=o.itemSelectable,u=o.placeholder,d=t.id,p=t.value,f=t.label,m=t.customProperties,v=t.active,g=t.disabled,_=t.highlighted,y=t.placeholder,E=Object.assign(document.createElement("div"),((n={className:a})[s?"innerHTML":"innerText"]=f,n));if(Object.assign(E.dataset,{item:"",id:d,value:p,customProperties:m}),v&&E.setAttribute("aria-selected","true"),g&&E.setAttribute("aria-disabled","true"),y&&E.classList.add(u),E.classList.add(_?l:h),i){g&&E.classList.remove(h),E.dataset.deletable="";var b="Remove item",S=Object.assign(document.createElement("button"),((r={type:"button",className:c})[s?"innerHTML":"innerText"]=b,r));S.setAttribute("aria-label","".concat(b,": '").concat(p,"'")),S.dataset.button="",E.appendChild(S)}return E},choiceList:function(e,t){var i=e.classNames.list,n=Object.assign(document.createElement("div"),{className:i});return t||n.setAttribute("aria-multiselectable","true"),n.setAttribute("role","listbox"),n},choiceGroup:function(e,t){var i,n=e.allowHTML,r=e.classNames,s=r.group,o=r.groupHeading,a=r.itemDisabled,c=t.id,l=t.value,h=t.disabled,u=Object.assign(document.createElement("div"),{className:"".concat(s," ").concat(h?a:"")});return u.setAttribute("role","group"),Object.assign(u.dataset,{group:"",id:c,value:l}),h&&u.setAttribute("aria-disabled","true"),u.appendChild(Object.assign(document.createElement("div"),((i={className:o})[n?"innerHTML":"innerText"]=l,i))),u},choice:function(e,t,i){var n,r=e.allowHTML,s=e.classNames,o=s.item,a=s.itemChoice,c=s.itemSelectable,l=s.selectedState,h=s.itemDisabled,u=s.placeholder,d=t.id,p=t.value,f=t.label,m=t.groupId,v=t.elementId,g=t.disabled,_=t.selected,y=t.placeholder,E=Object.assign(document.createElement("div"),((n={id:v})[r?"innerHTML":"innerText"]=f,n.className="".concat(o," ").concat(a),n));return _&&E.classList.add(l),y&&E.classList.add(u),E.setAttribute("role",m&&m>0?"treeitem":"option"),Object.assign(E.dataset,{choice:"",id:d,value:p,selectText:i}),g?(E.classList.add(h),E.dataset.choiceDisabled="",E.setAttribute("aria-disabled","true")):(E.classList.add(c),E.dataset.choiceSelectable=""),E},input:function(e,t){var i=e.classNames,n=i.input,r=i.inputCloned,s=Object.assign(document.createElement("input"),{type:"search",name:"search_terms",className:"".concat(n," ").concat(r),autocomplete:"off",autocapitalize:"off",spellcheck:!1});return s.setAttribute("role","textbox"),s.setAttribute("aria-autocomplete","list"),s.setAttribute("aria-label",t),s},dropdown:function(e){var t=e.classNames,i=t.list,n=t.listDropdown,r=document.createElement("div");return r.classList.add(i,n),r.setAttribute("aria-expanded","false"),r},notice:function(e,t,i){var n,r=e.allowHTML,s=e.classNames,o=s.item,a=s.itemChoice,c=s.noResults,l=s.noChoices;void 0===i&&(i="");var h=[o,a];return"no-choices"===i?h.push(l):"no-results"===i&&h.push(c),Object.assign(document.createElement("div"),((n={})[r?"innerHTML":"innerText"]=t,n.className=h.join(" "),n))},option:function(e){var t=e.label,i=e.value,n=e.customProperties,r=e.active,s=e.disabled,o=new Option(t,i,!1,r);return n&&(o.dataset.customProperties="".concat(n)),o.disabled=!!s,o}};t.default=i},996:function(e){var t=function(e){return function(e){return!!e&&"object"==typeof e}(e)&&!function(e){var t=Object.prototype.toString.call(e);return"[object RegExp]"===t||"[object Date]"===t||function(e){return e.$$typeof===i}(e)}(e)},i="function"==typeof Symbol&&Symbol.for?Symbol.for("react.element"):60103;function n(e,t){return!1!==t.clone&&t.isMergeableObject(e)?a((i=e,Array.isArray(i)?[]:{}),e,t):e;var i}function r(e,t,i){return e.concat(t).map((function(e){return n(e,i)}))}function s(e){return Object.keys(e).concat(function(e){return Object.getOwnPropertySymbols?Object.getOwnPropertySymbols(e).filter((function(t){return e.propertyIsEnumerable(t)})):[]}(e))}function o(e,t){try{return t in e}catch(e){return!1}}function a(e,i,c){(c=c||{}).arrayMerge=c.arrayMerge||r,c.isMergeableObject=c.isMergeableObject||t,c.cloneUnlessOtherwiseSpecified=n;var l=Array.isArray(i);return l===Array.isArray(e)?l?c.arrayMerge(e,i,c):function(e,t,i){var r={};return i.isMergeableObject(e)&&s(e).forEach((function(t){r[t]=n(e[t],i)})),s(t).forEach((function(s){(function(e,t){return o(e,t)&&!(Object.hasOwnProperty.call(e,t)&&Object.propertyIsEnumerable.call(e,t))})(e,s)||(o(e,s)&&i.isMergeableObject(t[s])?r[s]=function(e,t){if(!t.customMerge)return a;var i=t.customMerge(e);return"function"==typeof i?i:a}(s,i)(e[s],t[s],i):r[s]=n(t[s],i))})),r}(e,i,c):n(i,c)}a.all=function(e,t){if(!Array.isArray(e))throw new Error("first argument should be an array");return e.reduce((function(e,i){return a(e,i,t)}),{})};var c=a;e.exports=c},221:function(e,t,i){function n(e){return Array.isArray?Array.isArray(e):"[object Array]"===l(e)}function r(e){return"string"==typeof e}function s(e){return"number"==typeof e}function o(e){return"object"==typeof e}function a(e){return null!=e}function c(e){return!e.trim().length}function l(e){return null==e?void 0===e?"[object Undefined]":"[object Null]":Object.prototype.toString.call(e)}i.r(t),i.d(t,{default:function(){return R}});const h=Object.prototype.hasOwnProperty;class u{constructor(e){this._keys=[],this._keyMap={};let t=0;e.forEach((e=>{let i=d(e);t+=i.weight,this._keys.push(i),this._keyMap[i.id]=i,t+=i.weight})),this._keys.forEach((e=>{e.weight/=t}))}get(e){return this._keyMap[e]}keys(){return this._keys}toJSON(){return JSON.stringify(this._keys)}}function d(e){let t=null,i=null,s=null,o=1,a=null;if(r(e)||n(e))s=e,t=p(e),i=f(e);else{if(!h.call(e,"name"))throw new Error("Missing name property in key");const n=e.name;if(s=n,h.call(e,"weight")&&(o=e.weight,o<=0))throw new Error((e=>`Property 'weight' in key '${e}' must be a positive integer`)(n));t=p(n),i=f(n),a=e.getFn}return{path:t,id:i,weight:o,src:s,getFn:a}}function p(e){return n(e)?e:e.split(".")}function f(e){return n(e)?e.join("."):e}var m={isCaseSensitive:!1,includeScore:!1,keys:[],shouldSort:!0,sortFn:(e,t)=>e.score===t.score?e.idx<t.idx?-1:1:e.score<t.score?-1:1,includeMatches:!1,findAllMatches:!1,minMatchCharLength:1,location:0,threshold:.6,distance:100,useExtendedSearch:!1,getFn:function(e,t){let i=[],c=!1;const h=(e,t,u)=>{if(a(e))if(t[u]){const d=e[t[u]];if(!a(d))return;if(u===t.length-1&&(r(d)||s(d)||function(e){return!0===e||!1===e||function(e){return o(e)&&null!==e}(e)&&"[object Boolean]"==l(e)}(d)))i.push(function(e){return null==e?"":function(e){if("string"==typeof e)return e;let t=e+"";return"0"==t&&1/e==-1/0?"-0":t}(e)}(d));else if(n(d)){c=!0;for(let e=0,i=d.length;e<i;e+=1)h(d[e],t,u+1)}else t.length&&h(d,t,u+1)}else i.push(e)};return h(e,r(t)?t.split("."):t,0),c?i:i[0]},ignoreLocation:!1,ignoreFieldNorm:!1,fieldNormWeight:1};const v=/[^ ]+/g;class g{constructor({getFn:e=m.getFn,fieldNormWeight:t=m.fieldNormWeight}={}){this.norm=function(e=1,t=3){const i=new Map,n=Math.pow(10,t);return{get(t){const r=t.match(v).length;if(i.has(r))return i.get(r);const s=1/Math.pow(r,.5*e),o=parseFloat(Math.round(s*n)/n);return i.set(r,o),o},clear(){i.clear()}}}(t,3),this.getFn=e,this.isCreated=!1,this.setIndexRecords()}setSources(e=[]){this.docs=e}setIndexRecords(e=[]){this.records=e}setKeys(e=[]){this.keys=e,this._keysMap={},e.forEach(((e,t)=>{this._keysMap[e.id]=t}))}create(){!this.isCreated&&this.docs.length&&(this.isCreated=!0,r(this.docs[0])?this.docs.forEach(((e,t)=>{this._addString(e,t)})):this.docs.forEach(((e,t)=>{this._addObject(e,t)})),this.norm.clear())}add(e){const t=this.size();r(e)?this._addString(e,t):this._addObject(e,t)}removeAt(e){this.records.splice(e,1);for(let t=e,i=this.size();t<i;t+=1)this.records[t].i-=1}getValueForItemAtKeyId(e,t){return e[this._keysMap[t]]}size(){return this.records.length}_addString(e,t){if(!a(e)||c(e))return;let i={v:e,i:t,n:this.norm.get(e)};this.records.push(i)}_addObject(e,t){let i={i:t,$:{}};this.keys.forEach(((t,s)=>{let o=t.getFn?t.getFn(e):this.getFn(e,t.path);if(a(o))if(n(o)){let e=[];const t=[{nestedArrIndex:-1,value:o}];for(;t.length;){const{nestedArrIndex:i,value:s}=t.pop();if(a(s))if(r(s)&&!c(s)){let t={v:s,i:i,n:this.norm.get(s)};e.push(t)}else n(s)&&s.forEach(((e,i)=>{t.push({nestedArrIndex:i,value:e})}))}i.$[s]=e}else if(r(o)&&!c(o)){let e={v:o,n:this.norm.get(o)};i.$[s]=e}})),this.records.push(i)}toJSON(){return{keys:this.keys,records:this.records}}}function _(e,t,{getFn:i=m.getFn,fieldNormWeight:n=m.fieldNormWeight}={}){const r=new g({getFn:i,fieldNormWeight:n});return r.setKeys(e.map(d)),r.setSources(t),r.create(),r}function y(e,{errors:t=0,currentLocation:i=0,expectedLocation:n=0,distance:r=m.distance,ignoreLocation:s=m.ignoreLocation}={}){const o=t/e.length;if(s)return o;const a=Math.abs(n-i);return r?o+a/r:a?1:o}const E=32;function b(e){let t={};for(let i=0,n=e.length;i<n;i+=1){const r=e.charAt(i);t[r]=(t[r]||0)|1<<n-i-1}return t}class S{constructor(e,{location:t=m.location,threshold:i=m.threshold,distance:n=m.distance,includeMatches:r=m.includeMatches,findAllMatches:s=m.findAllMatches,minMatchCharLength:o=m.minMatchCharLength,isCaseSensitive:a=m.isCaseSensitive,ignoreLocation:c=m.ignoreLocation}={}){if(this.options={location:t,threshold:i,distance:n,includeMatches:r,findAllMatches:s,minMatchCharLength:o,isCaseSensitive:a,ignoreLocation:c},this.pattern=a?e:e.toLowerCase(),this.chunks=[],!this.pattern.length)return;const l=(e,t)=>{this.chunks.push({pattern:e,alphabet:b(e),startIndex:t})},h=this.pattern.length;if(h>E){let e=0;const t=h%E,i=h-t;for(;e<i;)l(this.pattern.substr(e,E),e),e+=E;if(t){const e=h-E;l(this.pattern.substr(e),e)}}else l(this.pattern,0)}searchIn(e){const{isCaseSensitive:t,includeMatches:i}=this.options;if(t||(e=e.toLowerCase()),this.pattern===e){let t={isMatch:!0,score:0};return i&&(t.indices=[[0,e.length-1]]),t}const{location:n,distance:r,threshold:s,findAllMatches:o,minMatchCharLength:a,ignoreLocation:c}=this.options;let l=[],h=0,u=!1;this.chunks.forEach((({pattern:t,alphabet:d,startIndex:p})=>{const{isMatch:f,score:v,indices:g}=function(e,t,i,{location:n=m.location,distance:r=m.distance,threshold:s=m.threshold,findAllMatches:o=m.findAllMatches,minMatchCharLength:a=m.minMatchCharLength,includeMatches:c=m.includeMatches,ignoreLocation:l=m.ignoreLocation}={}){if(t.length>E)throw new Error("Pattern length exceeds max of 32.");const h=t.length,u=e.length,d=Math.max(0,Math.min(n,u));let p=s,f=d;const v=a>1||c,g=v?Array(u):[];let _;for(;(_=e.indexOf(t,f))>-1;){let e=y(t,{currentLocation:_,expectedLocation:d,distance:r,ignoreLocation:l});if(p=Math.min(e,p),f=_+h,v){let e=0;for(;e<h;)g[_+e]=1,e+=1}}f=-1;let b=[],S=1,O=h+u;const I=1<<h-1;for(let n=0;n<h;n+=1){let s=0,a=O;for(;s<a;)y(t,{errors:n,currentLocation:d+a,expectedLocation:d,distance:r,ignoreLocation:l})<=p?s=a:O=a,a=Math.floor((O-s)/2+s);O=a;let c=Math.max(1,d-a+1),m=o?u:Math.min(d+a,u)+h,_=Array(m+2);_[m+1]=(1<<n)-1;for(let s=m;s>=c;s-=1){let o=s-1,a=i[e.charAt(o)];if(v&&(g[o]=+!!a),_[s]=(_[s+1]<<1|1)&a,n&&(_[s]|=(b[s+1]|b[s])<<1|1|b[s+1]),_[s]&I&&(S=y(t,{errors:n,currentLocation:o,expectedLocation:d,distance:r,ignoreLocation:l}),S<=p)){if(p=S,f=o,f<=d)break;c=Math.max(1,2*d-f)}}if(y(t,{errors:n+1,currentLocation:d,expectedLocation:d,distance:r,ignoreLocation:l})>p)break;b=_}const C={isMatch:f>=0,score:Math.max(.001,S)};if(v){const e=function(e=[],t=m.minMatchCharLength){let i=[],n=-1,r=-1,s=0;for(let o=e.length;s<o;s+=1){let o=e[s];o&&-1===n?n=s:o||-1===n||(r=s-1,r-n+1>=t&&i.push([n,r]),n=-1)}return e[s-1]&&s-n>=t&&i.push([n,s-1]),i}(g,a);e.length?c&&(C.indices=e):C.isMatch=!1}return C}(e,t,d,{location:n+p,distance:r,threshold:s,findAllMatches:o,minMatchCharLength:a,includeMatches:i,ignoreLocation:c});f&&(u=!0),h+=v,f&&g&&(l=[...l,...g])}));let d={isMatch:u,score:u?h/this.chunks.length:1};return u&&i&&(d.indices=l),d}}class O{constructor(e){this.pattern=e}static isMultiMatch(e){return I(e,this.multiRegex)}static isSingleMatch(e){return I(e,this.singleRegex)}search(){}}function I(e,t){const i=e.match(t);return i?i[1]:null}class C extends O{constructor(e,{location:t=m.location,threshold:i=m.threshold,distance:n=m.distance,includeMatches:r=m.includeMatches,findAllMatches:s=m.findAllMatches,minMatchCharLength:o=m.minMatchCharLength,isCaseSensitive:a=m.isCaseSensitive,ignoreLocation:c=m.ignoreLocation}={}){super(e),this._bitapSearch=new S(e,{location:t,threshold:i,distance:n,includeMatches:r,findAllMatches:s,minMatchCharLength:o,isCaseSensitive:a,ignoreLocation:c})}static get type(){return"fuzzy"}static get multiRegex(){return/^"(.*)"$/}static get singleRegex(){return/^(.*)$/}search(e){return this._bitapSearch.searchIn(e)}}class T extends O{constructor(e){super(e)}static get type(){return"include"}static get multiRegex(){return/^'"(.*)"$/}static get singleRegex(){return/^'(.*)$/}search(e){let t,i=0;const n=[],r=this.pattern.length;for(;(t=e.indexOf(this.pattern,i))>-1;)i=t+r,n.push([t,i-1]);const s=!!n.length;return{isMatch:s,score:s?0:1,indices:n}}}const L=[class extends O{constructor(e){super(e)}static get type(){return"exact"}static get multiRegex(){return/^="(.*)"$/}static get singleRegex(){return/^=(.*)$/}search(e){const t=e===this.pattern;return{isMatch:t,score:t?0:1,indices:[0,this.pattern.length-1]}}},T,class extends O{constructor(e){super(e)}static get type(){return"prefix-exact"}static get multiRegex(){return/^\^"(.*)"$/}static get singleRegex(){return/^\^(.*)$/}search(e){const t=e.startsWith(this.pattern);return{isMatch:t,score:t?0:1,indices:[0,this.pattern.length-1]}}},class extends O{constructor(e){super(e)}static get type(){return"inverse-prefix-exact"}static get multiRegex(){return/^!\^"(.*)"$/}static get singleRegex(){return/^!\^(.*)$/}search(e){const t=!e.startsWith(this.pattern);return{isMatch:t,score:t?0:1,indices:[0,e.length-1]}}},class extends O{constructor(e){super(e)}static get type(){return"inverse-suffix-exact"}static get multiRegex(){return/^!"(.*)"\$$/}static get singleRegex(){return/^!(.*)\$$/}search(e){const t=!e.endsWith(this.pattern);return{isMatch:t,score:t?0:1,indices:[0,e.length-1]}}},class extends O{constructor(e){super(e)}static get type(){return"suffix-exact"}static get multiRegex(){return/^"(.*)"\$$/}static get singleRegex(){return/^(.*)\$$/}search(e){const t=e.endsWith(this.pattern);return{isMatch:t,score:t?0:1,indices:[e.length-this.pattern.length,e.length-1]}}},class extends O{constructor(e){super(e)}static get type(){return"inverse-exact"}static get multiRegex(){return/^!"(.*)"$/}static get singleRegex(){return/^!(.*)$/}search(e){const t=-1===e.indexOf(this.pattern);return{isMatch:t,score:t?0:1,indices:[0,e.length-1]}}},C],w=L.length,A=/ +(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)/,M=new Set([C.type,T.type]);const P=[];function x(e,t){for(let i=0,n=P.length;i<n;i+=1){let n=P[i];if(n.condition(e,t))return new n(e,t)}return new S(e,t)}const N="$and",D=e=>!(!e.$and&&!e.$or),j=e=>({[N]:Object.keys(e).map((t=>({[t]:e[t]})))});function F(e,t,{auto:i=!0}={}){const s=e=>{let a=Object.keys(e);const c=(e=>!!e.$path)(e);if(!c&&a.length>1&&!D(e))return s(j(e));if((e=>!n(e)&&o(e)&&!D(e))(e)){const n=c?e.$path:a[0],s=c?e.$val:e[n];if(!r(s))throw new Error((e=>`Invalid value for key ${e}`)(n));const o={keyId:f(n),pattern:s};return i&&(o.searcher=x(s,t)),o}let l={children:[],operator:a[0]};return a.forEach((t=>{const i=e[t];n(i)&&i.forEach((e=>{l.children.push(s(e))}))})),l};return D(e)||(e=j(e)),s(e)}function k(e,t){const i=e.matches;t.matches=[],a(i)&&i.forEach((e=>{if(!a(e.indices)||!e.indices.length)return;const{indices:i,value:n}=e;let r={indices:i,value:n};e.key&&(r.key=e.key.src),e.idx>-1&&(r.refIndex=e.idx),t.matches.push(r)}))}function K(e,t){t.score=e.score}class R{constructor(e,t={},i){this.options={...m,...t},this.options.useExtendedSearch,this._keyStore=new u(this.options.keys),this.setCollection(e,i)}setCollection(e,t){if(this._docs=e,t&&!(t instanceof g))throw new Error("Incorrect 'index' type");this._myIndex=t||_(this.options.keys,this._docs,{getFn:this.options.getFn,fieldNormWeight:this.options.fieldNormWeight})}add(e){a(e)&&(this._docs.push(e),this._myIndex.add(e))}remove(e=(()=>!1)){const t=[];for(let i=0,n=this._docs.length;i<n;i+=1){const r=this._docs[i];e(r,i)&&(this.removeAt(i),i-=1,n-=1,t.push(r))}return t}removeAt(e){this._docs.splice(e,1),this._myIndex.removeAt(e)}getIndex(){return this._myIndex}search(e,{limit:t=-1}={}){const{includeMatches:i,includeScore:n,shouldSort:o,sortFn:a,ignoreFieldNorm:c}=this.options;let l=r(e)?r(this._docs[0])?this._searchStringList(e):this._searchObjectList(e):this._searchLogical(e);return function(e,{ignoreFieldNorm:t=m.ignoreFieldNorm}){e.forEach((e=>{let i=1;e.matches.forEach((({key:e,norm:n,score:r})=>{const s=e?e.weight:null;i*=Math.pow(0===r&&s?Number.EPSILON:r,(s||1)*(t?1:n))})),e.score=i}))}(l,{ignoreFieldNorm:c}),o&&l.sort(a),s(t)&&t>-1&&(l=l.slice(0,t)),function(e,t,{includeMatches:i=m.includeMatches,includeScore:n=m.includeScore}={}){const r=[];return i&&r.push(k),n&&r.push(K),e.map((e=>{const{idx:i}=e,n={item:t[i],refIndex:i};return r.length&&r.forEach((t=>{t(e,n)})),n}))}(l,this._docs,{includeMatches:i,includeScore:n})}_searchStringList(e){const t=x(e,this.options),{records:i}=this._myIndex,n=[];return i.forEach((({v:e,i:i,n:r})=>{if(!a(e))return;const{isMatch:s,score:o,indices:c}=t.searchIn(e);s&&n.push({item:e,idx:i,matches:[{score:o,value:e,norm:r,indices:c}]})})),n}_searchLogical(e){const t=F(e,this.options),i=(e,t,n)=>{if(!e.children){const{keyId:i,searcher:r}=e,s=this._findMatches({key:this._keyStore.get(i),value:this._myIndex.getValueForItemAtKeyId(t,i),searcher:r});return s&&s.length?[{idx:n,item:t,matches:s}]:[]}const r=[];for(let s=0,o=e.children.length;s<o;s+=1){const o=e.children[s],a=i(o,t,n);if(a.length)r.push(...a);else if(e.operator===N)return[]}return r},n=this._myIndex.records,r={},s=[];return n.forEach((({$:e,i:n})=>{if(a(e)){let o=i(t,e,n);o.length&&(r[n]||(r[n]={idx:n,item:e,matches:[]},s.push(r[n])),o.forEach((({matches:e})=>{r[n].matches.push(...e)})))}})),s}_searchObjectList(e){const t=x(e,this.options),{keys:i,records:n}=this._myIndex,r=[];return n.forEach((({$:e,i:n})=>{if(!a(e))return;let s=[];i.forEach(((i,n)=>{s.push(...this._findMatches({key:i,value:e[n],searcher:t}))})),s.length&&r.push({idx:n,item:e,matches:s})})),r}_findMatches({key:e,value:t,searcher:i}){if(!a(t))return[];let r=[];if(n(t))t.forEach((({v:t,i:n,n:s})=>{if(!a(t))return;const{isMatch:o,score:c,indices:l}=i.searchIn(t);o&&r.push({score:c,key:e,value:t,idx:n,norm:s,indices:l})}));else{const{v:n,n:s}=t,{isMatch:o,score:a,indices:c}=i.searchIn(n);o&&r.push({score:a,key:e,value:n,norm:s,indices:c})}return r}}R.version="6.6.2",R.createIndex=_,R.parseIndex=function(e,{getFn:t=m.getFn,fieldNormWeight:i=m.fieldNormWeight}={}){const{keys:n,records:r}=e,s=new g({getFn:t,fieldNormWeight:i});return s.setKeys(n),s.setIndexRecords(r),s},R.config=m,R.parseQuery=F,function(...e){P.push(...e)}(class{constructor(e,{isCaseSensitive:t=m.isCaseSensitive,includeMatches:i=m.includeMatches,minMatchCharLength:n=m.minMatchCharLength,ignoreLocation:r=m.ignoreLocation,findAllMatches:s=m.findAllMatches,location:o=m.location,threshold:a=m.threshold,distance:c=m.distance}={}){this.query=null,this.options={isCaseSensitive:t,includeMatches:i,minMatchCharLength:n,findAllMatches:s,ignoreLocation:r,location:o,threshold:a,distance:c},this.pattern=t?e:e.toLowerCase(),this.query=function(e,t={}){return e.split("|").map((e=>{let i=e.trim().split(A).filter((e=>e&&!!e.trim())),n=[];for(let e=0,r=i.length;e<r;e+=1){const r=i[e];let s=!1,o=-1;for(;!s&&++o<w;){const e=L[o];let i=e.isMultiMatch(r);i&&(n.push(new e(i,t)),s=!0)}if(!s)for(o=-1;++o<w;){const e=L[o];let i=e.isSingleMatch(r);if(i){n.push(new e(i,t));break}}}return n}))}(this.pattern,this.options)}static condition(e,t){return t.useExtendedSearch}searchIn(e){const t=this.query;if(!t)return{isMatch:!1,score:1};const{includeMatches:i,isCaseSensitive:n}=this.options;e=n?e:e.toLowerCase();let r=0,s=[],o=0;for(let n=0,a=t.length;n<a;n+=1){const a=t[n];s.length=0,r=0;for(let t=0,n=a.length;t<n;t+=1){const n=a[t],{isMatch:c,indices:l,score:h}=n.search(e);if(!c){o=0,r=0,s.length=0;break}if(r+=1,o+=h,i){const e=n.constructor.type;M.has(e)?s=[...s,...l]:s.push(l)}}if(r){let e={isMatch:!0,score:o/r};return i&&(e.indices=s),e}}return{isMatch:!1,score:1}}})},791:function(e,t,i){function n(e){return n="function"==typeof Symbol&&"symbol"==typeof Symbol.iterator?function(e){return typeof e}:function(e){return e&&"function"==typeof Symbol&&e.constructor===Symbol&&e!==Symbol.prototype?"symbol":typeof e},n(e)}function r(e,t,i){return(t=function(e){var t=function(e,t){if("object"!==n(e)||null===e)return e;var i=e[Symbol.toPrimitive];if(void 0!==i){var r=i.call(e,t);if("object"!==n(r))return r;throw new TypeError("@@toPrimitive must return a primitive value.")}return String(e)}(e,"string");return"symbol"===n(t)?t:String(t)}(t))in e?Object.defineProperty(e,t,{value:i,enumerable:!0,configurable:!0,writable:!0}):e[t]=i,e}function s(e,t){var i=Object.keys(e);if(Object.getOwnPropertySymbols){var n=Object.getOwnPropertySymbols(e);t&&(n=n.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),i.push.apply(i,n)}return i}function o(e){for(var t=1;t<arguments.length;t++){var i=null!=arguments[t]?arguments[t]:{};t%2?s(Object(i),!0).forEach((function(t){r(e,t,i[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(i)):s(Object(i)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(i,t))}))}return e}function a(e){return"Minified Redux error #"+e+"; visit https://redux.js.org/Errors?code="+e+" for the full message or use the non-minified dev environment for full errors. "}i.r(t),i.d(t,{__DO_NOT_USE__ActionTypes:function(){return h},applyMiddleware:function(){return _},bindActionCreators:function(){return v},combineReducers:function(){return f},compose:function(){return g},createStore:function(){return d},legacy_createStore:function(){return p}});var c="function"==typeof Symbol&&Symbol.observable||"@@observable",l=function(){return Math.random().toString(36).substring(7).split("").join(".")},h={INIT:"@@redux/INIT"+l(),REPLACE:"@@redux/REPLACE"+l(),PROBE_UNKNOWN_ACTION:function(){return"@@redux/PROBE_UNKNOWN_ACTION"+l()}};function u(e){if("object"!=typeof e||null===e)return!1;for(var t=e;null!==Object.getPrototypeOf(t);)t=Object.getPrototypeOf(t);return Object.getPrototypeOf(e)===t}function d(e,t,i){var n;if("function"==typeof t&&"function"==typeof i||"function"==typeof i&&"function"==typeof arguments[3])throw new Error(a(0));if("function"==typeof t&&void 0===i&&(i=t,t=void 0),void 0!==i){if("function"!=typeof i)throw new Error(a(1));return i(d)(e,t)}if("function"!=typeof e)throw new Error(a(2));var r=e,s=t,o=[],l=o,p=!1;function f(){l===o&&(l=o.slice())}function m(){if(p)throw new Error(a(3));return s}function v(e){if("function"!=typeof e)throw new Error(a(4));if(p)throw new Error(a(5));var t=!0;return f(),l.push(e),function(){if(t){if(p)throw new Error(a(6));t=!1,f();var i=l.indexOf(e);l.splice(i,1),o=null}}}function g(e){if(!u(e))throw new Error(a(7));if(void 0===e.type)throw new Error(a(8));if(p)throw new Error(a(9));try{p=!0,s=r(s,e)}finally{p=!1}for(var t=o=l,i=0;i<t.length;i++)(0,t[i])();return e}function _(e){if("function"!=typeof e)throw new Error(a(10));r=e,g({type:h.REPLACE})}function y(){var e,t=v;return(e={subscribe:function(e){if("object"!=typeof e||null===e)throw new Error(a(11));function i(){e.next&&e.next(m())}return i(),{unsubscribe:t(i)}}})[c]=function(){return this},e}return g({type:h.INIT}),(n={dispatch:g,subscribe:v,getState:m,replaceReducer:_})[c]=y,n}var p=d;function f(e){for(var t=Object.keys(e),i={},n=0;n<t.length;n++){var r=t[n];"function"==typeof e[r]&&(i[r]=e[r])}var s,o=Object.keys(i);try{!function(e){Object.keys(e).forEach((function(t){var i=e[t];if(void 0===i(void 0,{type:h.INIT}))throw new Error(a(12));if(void 0===i(void 0,{type:h.PROBE_UNKNOWN_ACTION()}))throw new Error(a(13))}))}(i)}catch(e){s=e}return function(e,t){if(void 0===e&&(e={}),s)throw s;for(var n=!1,r={},c=0;c<o.length;c++){var l=o[c],h=i[l],u=e[l],d=h(u,t);if(void 0===d)throw t&&t.type,new Error(a(14));r[l]=d,n=n||d!==u}return(n=n||o.length!==Object.keys(e).length)?r:e}}function m(e,t){return function(){return t(e.apply(this,arguments))}}function v(e,t){if("function"==typeof e)return m(e,t);if("object"!=typeof e||null===e)throw new Error(a(16));var i={};for(var n in e){var r=e[n];"function"==typeof r&&(i[n]=m(r,t))}return i}function g(){for(var e=arguments.length,t=new Array(e),i=0;i<e;i++)t[i]=arguments[i];return 0===t.length?function(e){return e}:1===t.length?t[0]:t.reduce((function(e,t){return function(){return e(t.apply(void 0,arguments))}}))}function _(){for(var e=arguments.length,t=new Array(e),i=0;i<e;i++)t[i]=arguments[i];return function(e){return function(){var i=e.apply(void 0,arguments),n=function(){throw new Error(a(15))},r={getState:i.getState,dispatch:function(){return n.apply(void 0,arguments)}},s=t.map((function(e){return e(r)}));return n=g.apply(void 0,s)(i.dispatch),o(o({},i),{},{dispatch:n})}}}}},t={};function i(n){var r=t[n];if(void 0!==r)return r.exports;var s=t[n]={exports:{}};return e[n].call(s.exports,s,s.exports,i),s.exports}i.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return i.d(t,{a:t}),t},i.d=function(e,t){for(var n in t)i.o(t,n)&&!i.o(e,n)&&Object.defineProperty(e,n,{enumerable:!0,get:t[n]})},i.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},i.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})};var n,r,s={};n=i(373),r=i.n(n),i(187),i(883),i(789),i(686),s.default=r(),window.Choices=s.default}();
!function(){function e(e){return e&&e.__esModule?e.default:e}function t(e){if(void 0===e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return e}function i(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function n(e,t){for(var i=0;i<t.length;i++){var n=t[i];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(e,n.key,n)}}function r(e,t,i){return t&&n(e.prototype,t),i&&n(e,i),e}function a(e){return a=Object.setPrototypeOf?Object.getPrototypeOf:function(e){return e.__proto__||Object.getPrototypeOf(e)},a(e)}function o(e,t){return o=Object.setPrototypeOf||function(e,t){return e.__proto__=t,e},o(e,t)}function l(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function");e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,writable:!0,configurable:!0}}),t&&o(e,t)}function s(e,i){return!i||"object"!=((n=i)&&n.constructor===Symbol?"symbol":typeof n)&&"function"!=typeof i?t(e):i;var n}var u;function c(e){return Array.isArray(e)||"[object Object]"=={}.toString.call(e)}function d(e){return!e||"object"!=typeof e&&"function"!=typeof e}u=function e(){var t=[].slice.call(arguments),i=!1;"boolean"==typeof t[0]&&(i=t.shift());var n=t[0];if(d(n))throw new Error("extendee must be an object");for(var r=t.slice(1),a=r.length,o=0;o<a;o++){var l=r[o];for(var s in l)if(Object.prototype.hasOwnProperty.call(l,s)){var u=l[s];if(i&&c(u)){var h=Array.isArray(u)?[]:{};n[s]=e(!0,Object.prototype.hasOwnProperty.call(n,s)&&!d(n[s])?n[s]:h,u)}else n[s]=u}}return n};var h=function(){"use strict";function e(){i(this,e)}return r(e,[{key:"on",value:function(e,t){return this._callbacks=this._callbacks||{},this._callbacks[e]||(this._callbacks[e]=[]),this._callbacks[e].push(t),this}},{key:"emit",value:function(e){for(var t=arguments.length,i=new Array(t>1?t-1:0),n=1;n<t;n++)i[n-1]=arguments[n];this._callbacks=this._callbacks||{};var r=this._callbacks[e],a=!0,o=!1,l=void 0;if(r)try{for(var s,u=r[Symbol.iterator]();!(a=(s=u.next()).done);a=!0){var c=s.value;c.apply(this,i)}}catch(e){o=!0,l=e}finally{try{a||null==u.return||u.return()}finally{if(o)throw l}}return this.element&&this.element.dispatchEvent(this.makeEvent("dropzone:"+e,{args:i})),this}},{key:"makeEvent",value:function(e,t){var i={bubbles:!0,cancelable:!0,detail:t};if("function"==typeof window.CustomEvent)return new CustomEvent(e,i);var n=document.createEvent("CustomEvent");return n.initCustomEvent(e,i.bubbles,i.cancelable,i.detail),n}},{key:"off",value:function(e,t){if(!this._callbacks||0===arguments.length)return this._callbacks={},this;var i=this._callbacks[e];if(!i)return this;if(1===arguments.length)return delete this._callbacks[e],this;for(var n=0;n<i.length;n++){var r=i[n];if(r===t){i.splice(n,1);break}}return this}}]),e}();var p={url:null,method:"post",withCredentials:!1,timeout:null,parallelUploads:2,uploadMultiple:!1,chunking:!1,forceChunking:!1,chunkSize:2097152,parallelChunkUploads:!1,retryChunks:!1,retryChunksLimit:3,maxFilesize:256,paramName:"file",createImageThumbnails:!0,maxThumbnailFilesize:10,thumbnailWidth:120,thumbnailHeight:120,thumbnailMethod:"crop",resizeWidth:null,resizeHeight:null,resizeMimeType:null,resizeQuality:.8,resizeMethod:"contain",filesizeBase:1e3,maxFiles:null,headers:null,defaultHeaders:!0,clickable:!0,ignoreHiddenFiles:!0,acceptedFiles:null,acceptedMimeTypes:null,autoProcessQueue:!0,autoQueue:!0,addRemoveLinks:!1,previewsContainer:null,disablePreviews:!1,hiddenInputContainer:"body",capture:null,renameFilename:null,renameFile:null,forceFallback:!1,dictDefaultMessage:"Drop files here to upload",dictFallbackMessage:"Your browser does not support drag'n'drop file uploads.",dictFallbackText:"Please use the fallback form below to upload your files like in the olden days.",dictFileTooBig:"File is too big ({{filesize}}MiB). Max filesize: {{maxFilesize}}MiB.",dictInvalidFileType:"You can't upload files of this type.",dictResponseError:"Server responded with {{statusCode}} code.",dictCancelUpload:"Cancel upload",dictUploadCanceled:"Upload canceled.",dictCancelUploadConfirmation:"Are you sure you want to cancel this upload?",dictRemoveFile:"Remove file",dictRemoveFileConfirmation:null,dictMaxFilesExceeded:"You can not upload any more files.",dictFileSizeUnits:{tb:"TB",gb:"GB",mb:"MB",kb:"KB",b:"b"},init:function(){},params:function(e,t,i){if(i)return{dzuuid:i.file.upload.uuid,dzchunkindex:i.index,dztotalfilesize:i.file.size,dzchunksize:this.options.chunkSize,dztotalchunkcount:i.file.upload.totalChunkCount,dzchunkbyteoffset:i.index*this.options.chunkSize}},accept:function(e,t){return t()},chunksUploaded:function(e,t){t()},binaryBody:!1,fallback:function(){var e;this.element.className="".concat(this.element.className," dz-browser-not-supported");var t=!0,i=!1,n=void 0;try{for(var r,a=this.element.getElementsByTagName("div")[Symbol.iterator]();!(t=(r=a.next()).done);t=!0){var o=r.value;if(/(^| )dz-message($| )/.test(o.className)){e=o,o.className="dz-message";break}}}catch(e){i=!0,n=e}finally{try{t||null==a.return||a.return()}finally{if(i)throw n}}e||(e=f.createElement('<div class="dz-message"><span></span></div>'),this.element.appendChild(e));var l=e.getElementsByTagName("span")[0];return l&&(null!=l.textContent?l.textContent=this.options.dictFallbackMessage:null!=l.innerText&&(l.innerText=this.options.dictFallbackMessage)),this.element.appendChild(this.getFallbackForm())},resize:function(e,t,i,n){var r={srcX:0,srcY:0,srcWidth:e.width,srcHeight:e.height},a=e.width/e.height;null==t&&null==i?(t=r.srcWidth,i=r.srcHeight):null==t?t=i*a:null==i&&(i=t/a);var o=(t=Math.min(t,r.srcWidth))/(i=Math.min(i,r.srcHeight));if(r.srcWidth>t||r.srcHeight>i)if("crop"===n)a>o?(r.srcHeight=e.height,r.srcWidth=r.srcHeight*o):(r.srcWidth=e.width,r.srcHeight=r.srcWidth/o);else{if("contain"!==n)throw new Error("Unknown resizeMethod '".concat(n,"'"));a>o?i=t/a:t=i*a}return r.srcX=(e.width-r.srcWidth)/2,r.srcY=(e.height-r.srcHeight)/2,r.trgWidth=t,r.trgHeight=i,r},transformFile:function(e,t){return(this.options.resizeWidth||this.options.resizeHeight)&&e.type.match(/image.*/)?this.resizeImage(e,this.options.resizeWidth,this.options.resizeHeight,this.options.resizeMethod,t):t(e)},previewTemplate:e('<div class="dz-file-preview dz-preview"> <div class="dz-image"><img data-dz-thumbnail=""></div> <div class="dz-details"> <div class="dz-size"><span data-dz-size=""></span></div> <div class="dz-filename"><span data-dz-name=""></span></div> </div> <div class="dz-progress"> <span class="dz-upload" data-dz-uploadprogress=""></span> </div> <div class="dz-error-message"><span data-dz-errormessage=""></span></div> <div class="dz-success-mark"> <svg width="54" height="54" fill="#fff"><path d="m10.207 29.793 4.086-4.086a1 1 0 0 1 1.414 0l5.586 5.586a1 1 0 0 0 1.414 0l15.586-15.586a1 1 0 0 1 1.414 0l4.086 4.086a1 1 0 0 1 0 1.414L22.707 42.293a1 1 0 0 1-1.414 0L10.207 31.207a1 1 0 0 1 0-1.414Z"/></svg> </div> <div class="dz-error-mark"> <svg width="54" height="54" fill="#fff"><path d="m26.293 20.293-7.086-7.086a1 1 0 0 0-1.414 0l-4.586 4.586a1 1 0 0 0 0 1.414l7.086 7.086a1 1 0 0 1 0 1.414l-7.086 7.086a1 1 0 0 0 0 1.414l4.586 4.586a1 1 0 0 0 1.414 0l7.086-7.086a1 1 0 0 1 1.414 0l7.086 7.086a1 1 0 0 0 1.414 0l4.586-4.586a1 1 0 0 0 0-1.414l-7.086-7.086a1 1 0 0 1 0-1.414l7.086-7.086a1 1 0 0 0 0-1.414l-4.586-4.586a1 1 0 0 0-1.414 0l-7.086 7.086a1 1 0 0 1-1.414 0Z"/></svg> </div> </div>'),drop:function(e){return this.element.classList.remove("dz-drag-hover")},dragstart:function(e){},dragend:function(e){return this.element.classList.remove("dz-drag-hover")},dragenter:function(e){return this.element.classList.add("dz-drag-hover")},dragover:function(e){return this.element.classList.add("dz-drag-hover")},dragleave:function(e){return this.element.classList.remove("dz-drag-hover")},paste:function(e){},reset:function(){return this.element.classList.remove("dz-started")},addedfile:function(e){if(this.element===this.previewsContainer&&this.element.classList.add("dz-started"),this.previewsContainer&&!this.options.disablePreviews){var t=this;e.previewElement=f.createElement(this.options.previewTemplate.trim()),e.previewTemplate=e.previewElement,this.previewsContainer.appendChild(e.previewElement);var i=!0,n=!1,r=void 0;try{for(var a,o=e.previewElement.querySelectorAll("[data-dz-name]")[Symbol.iterator]();!(i=(a=o.next()).done);i=!0){var l=a.value;l.textContent=e.name}}catch(e){n=!0,r=e}finally{try{i||null==o.return||o.return()}finally{if(n)throw r}}var s=!0,u=!1,c=void 0;try{for(var d,h=e.previewElement.querySelectorAll("[data-dz-size]")[Symbol.iterator]();!(s=(d=h.next()).done);s=!0)(l=d.value).innerHTML=this.filesize(e.size)}catch(e){u=!0,c=e}finally{try{s||null==h.return||h.return()}finally{if(u)throw c}}this.options.addRemoveLinks&&(e._removeLink=f.createElement('<a class="dz-remove" href="javascript:undefined;" data-dz-remove>'.concat(this.options.dictRemoveFile,"</a>")),e.previewElement.appendChild(e._removeLink));var p=function(i){var n=t;if(i.preventDefault(),i.stopPropagation(),e.status===f.UPLOADING)return f.confirm(t.options.dictCancelUploadConfirmation,(function(){return n.removeFile(e)}));var r=t;return t.options.dictRemoveFileConfirmation?f.confirm(t.options.dictRemoveFileConfirmation,(function(){return r.removeFile(e)})):t.removeFile(e)},m=!0,v=!1,y=void 0;try{for(var g,b=e.previewElement.querySelectorAll("[data-dz-remove]")[Symbol.iterator]();!(m=(g=b.next()).done);m=!0){g.value.addEventListener("click",p)}}catch(e){v=!0,y=e}finally{try{m||null==b.return||b.return()}finally{if(v)throw y}}}},removedfile:function(e){return null!=e.previewElement&&null!=e.previewElement.parentNode&&e.previewElement.parentNode.removeChild(e.previewElement),this._updateMaxFilesReachedClass()},thumbnail:function(e,t){if(e.previewElement){e.previewElement.classList.remove("dz-file-preview");var i=!0,n=!1,r=void 0;try{for(var a,o=e.previewElement.querySelectorAll("[data-dz-thumbnail]")[Symbol.iterator]();!(i=(a=o.next()).done);i=!0){var l=a.value;l.alt=e.name,l.src=t}}catch(e){n=!0,r=e}finally{try{i||null==o.return||o.return()}finally{if(n)throw r}}return setTimeout((function(){return e.previewElement.classList.add("dz-image-preview")}),1)}},error:function(e,t){if(e.previewElement){e.previewElement.classList.add("dz-error"),"string"!=typeof t&&t.error&&(t=t.error);var i=!0,n=!1,r=void 0;try{for(var a,o=e.previewElement.querySelectorAll("[data-dz-errormessage]")[Symbol.iterator]();!(i=(a=o.next()).done);i=!0){a.value.textContent=t}}catch(e){n=!0,r=e}finally{try{i||null==o.return||o.return()}finally{if(n)throw r}}}},errormultiple:function(){},processing:function(e){if(e.previewElement&&(e.previewElement.classList.add("dz-processing"),e._removeLink))return e._removeLink.innerHTML=this.options.dictCancelUpload},processingmultiple:function(){},uploadprogress:function(e,t,i){var n=!0,r=!1,a=void 0;if(e.previewElement)try{for(var o,l=e.previewElement.querySelectorAll("[data-dz-uploadprogress]")[Symbol.iterator]();!(n=(o=l.next()).done);n=!0){var s=o.value;"PROGRESS"===s.nodeName?s.value=t:s.style.width="".concat(t,"%")}}catch(e){r=!0,a=e}finally{try{n||null==l.return||l.return()}finally{if(r)throw a}}},totaluploadprogress:function(){},sending:function(){},sendingmultiple:function(){},success:function(e){if(e.previewElement)return e.previewElement.classList.add("dz-success")},successmultiple:function(){},canceled:function(e){return this.emit("error",e,this.options.dictUploadCanceled)},canceledmultiple:function(){},complete:function(e){if(e._removeLink&&(e._removeLink.innerHTML=this.options.dictRemoveFile),e.previewElement)return e.previewElement.classList.add("dz-complete")},completemultiple:function(){},maxfilesexceeded:function(){},maxfilesreached:function(){},queuecomplete:function(){},addedfiles:function(){}},f=function(n){"use strict";function o(n,r){var l,c,d,h;if(i(this,o),(l=s(this,(c=o,a(c)).call(this))).element=n,l.clickableElements=[],l.listeners=[],l.files=[],"string"==typeof l.element&&(l.element=document.querySelector(l.element)),!l.element||null==l.element.nodeType)throw new Error("Invalid dropzone element.");if(l.element.dropzone)throw new Error("Dropzone already attached.");o.instances.push(t(l)),l.element.dropzone=t(l);var f=null!=(h=o.optionsForElement(l.element))?h:{};if(l.options=e(u)(!0,{},p,f,null!=r?r:{}),l.options.previewTemplate=l.options.previewTemplate.replace(/\n*/g,""),l.options.forceFallback||!o.isBrowserSupported())return s(l,l.options.fallback.call(t(l)));if(null==l.options.url&&(l.options.url=l.element.getAttribute("action")),!l.options.url)throw new Error("No URL provided.");if(l.options.acceptedFiles&&l.options.acceptedMimeTypes)throw new Error("You can't provide both 'acceptedFiles' and 'acceptedMimeTypes'. 'acceptedMimeTypes' is deprecated.");if(l.options.uploadMultiple&&l.options.chunking)throw new Error("You cannot set both: uploadMultiple and chunking.");if(l.options.binaryBody&&l.options.uploadMultiple)throw new Error("You cannot set both: binaryBody and uploadMultiple.");return l.options.acceptedMimeTypes&&(l.options.acceptedFiles=l.options.acceptedMimeTypes,delete l.options.acceptedMimeTypes),null!=l.options.renameFilename&&(l.options.renameFile=function(e){return l.options.renameFilename.call(t(l),e.name,e)}),"string"==typeof l.options.method&&(l.options.method=l.options.method.toUpperCase()),(d=l.getExistingFallback())&&d.parentNode&&d.parentNode.removeChild(d),!1!==l.options.previewsContainer&&(l.options.previewsContainer?l.previewsContainer=o.getElement(l.options.previewsContainer,"previewsContainer"):l.previewsContainer=l.element),l.options.clickable&&(!0===l.options.clickable?l.clickableElements=[l.element]:l.clickableElements=o.getElements(l.options.clickable,"clickable")),l.init(),l}return l(o,n),r(o,[{key:"getAcceptedFiles",value:function(){return this.files.filter((function(e){return e.accepted})).map((function(e){return e}))}},{key:"getRejectedFiles",value:function(){return this.files.filter((function(e){return!e.accepted})).map((function(e){return e}))}},{key:"getFilesWithStatus",value:function(e){return this.files.filter((function(t){return t.status===e})).map((function(e){return e}))}},{key:"getQueuedFiles",value:function(){return this.getFilesWithStatus(o.QUEUED)}},{key:"getUploadingFiles",value:function(){return this.getFilesWithStatus(o.UPLOADING)}},{key:"getAddedFiles",value:function(){return this.getFilesWithStatus(o.ADDED)}},{key:"getActiveFiles",value:function(){return this.files.filter((function(e){return e.status===o.UPLOADING||e.status===o.QUEUED})).map((function(e){return e}))}},{key:"init",value:function(){var e=this,t=this,i=this,n=this,r=this,a=this,l=this,s=this,u=this,c=this,d=this;if("form"===this.element.tagName&&this.element.setAttribute("enctype","multipart/form-data"),this.element.classList.contains("dropzone")&&!this.element.querySelector(".dz-message")&&this.element.appendChild(o.createElement('<div class="dz-default dz-message"><button class="dz-button" type="button">'.concat(this.options.dictDefaultMessage,"</button></div>"))),this.clickableElements.length){var h=this,p=function(){var e=h;h.hiddenFileInput&&h.hiddenFileInput.parentNode.removeChild(h.hiddenFileInput),h.hiddenFileInput=document.createElement("input"),h.hiddenFileInput.setAttribute("type","file"),(null===h.options.maxFiles||h.options.maxFiles>1)&&h.hiddenFileInput.setAttribute("multiple","multiple"),h.hiddenFileInput.className="dz-hidden-input",null!==h.options.acceptedFiles&&h.hiddenFileInput.setAttribute("accept",h.options.acceptedFiles),null!==h.options.capture&&h.hiddenFileInput.setAttribute("capture",h.options.capture),h.hiddenFileInput.setAttribute("tabindex","-1"),h.hiddenFileInput.style.visibility="hidden",h.hiddenFileInput.style.position="absolute",h.hiddenFileInput.style.top="0",h.hiddenFileInput.style.left="0",h.hiddenFileInput.style.height="0",h.hiddenFileInput.style.width="0",o.getElement(h.options.hiddenInputContainer,"hiddenInputContainer").appendChild(h.hiddenFileInput),h.hiddenFileInput.addEventListener("change",(function(){var t=e.hiddenFileInput.files,i=!0,n=!1,r=void 0;if(t.length)try{for(var a,o=t[Symbol.iterator]();!(i=(a=o.next()).done);i=!0){var l=a.value;e.addFile(l)}}catch(e){n=!0,r=e}finally{try{i||null==o.return||o.return()}finally{if(n)throw r}}e.emit("addedfiles",t),p()}))};p()}this.URL=null!==window.URL?window.URL:window.webkitURL;var f=!0,m=!1,v=void 0;try{for(var y,g=this.events[Symbol.iterator]();!(f=(y=g.next()).done);f=!0){var b=y.value;this.on(b,this.options[b])}}catch(e){m=!0,v=e}finally{try{f||null==g.return||g.return()}finally{if(m)throw v}}this.on("uploadprogress",(function(){return e.updateTotalUploadProgress()})),this.on("removedfile",(function(){return t.updateTotalUploadProgress()})),this.on("canceled",(function(e){return i.emit("complete",e)})),this.on("complete",(function(e){var t=n;if(0===n.getAddedFiles().length&&0===n.getUploadingFiles().length&&0===n.getQueuedFiles().length)return setTimeout((function(){return t.emit("queuecomplete")}),0)}));var k=function(e){if(function(e){if(e.dataTransfer.types)for(var t=0;t<e.dataTransfer.types.length;t++)if("Files"===e.dataTransfer.types[t])return!0;return!1}(e))return e.stopPropagation(),e.preventDefault?e.preventDefault():e.returnValue=!1};return this.listeners=[{element:this.element,events:{dragstart:function(e){return r.emit("dragstart",e)},dragenter:function(e){return k(e),a.emit("dragenter",e)},dragover:function(e){var t;try{t=e.dataTransfer.effectAllowed}catch(e){}return e.dataTransfer.dropEffect="move"===t||"linkMove"===t?"move":"copy",k(e),l.emit("dragover",e)},dragleave:function(e){return s.emit("dragleave",e)},drop:function(e){return k(e),u.drop(e)},dragend:function(e){return c.emit("dragend",e)}}}],this.clickableElements.forEach((function(e){var t=d;return d.listeners.push({element:e,events:{click:function(i){return(e!==t.element||i.target===t.element||o.elementInside(i.target,t.element.querySelector(".dz-message")))&&t.hiddenFileInput.click(),!0}}})})),this.enable(),this.options.init.call(this)}},{key:"destroy",value:function(){return this.disable(),this.removeAllFiles(!0),(null!=this.hiddenFileInput?this.hiddenFileInput.parentNode:void 0)&&(this.hiddenFileInput.parentNode.removeChild(this.hiddenFileInput),this.hiddenFileInput=null),delete this.element.dropzone,o.instances.splice(o.instances.indexOf(this),1)}},{key:"updateTotalUploadProgress",value:function(){var e,t=0,i=0;if(this.getActiveFiles().length){var n=!0,r=!1,a=void 0;try{for(var o,l=this.getActiveFiles()[Symbol.iterator]();!(n=(o=l.next()).done);n=!0){var s=o.value;t+=s.upload.bytesSent,i+=s.upload.total}}catch(e){r=!0,a=e}finally{try{n||null==l.return||l.return()}finally{if(r)throw a}}e=100*t/i}else e=100;return this.emit("totaluploadprogress",e,i,t)}},{key:"_getParamName",value:function(e){return"function"==typeof this.options.paramName?this.options.paramName(e):"".concat(this.options.paramName).concat(this.options.uploadMultiple?"[".concat(e,"]"):"")}},{key:"_renameFile",value:function(e){return"function"!=typeof this.options.renameFile?e.name:this.options.renameFile(e)}},{key:"getFallbackForm",value:function(){var e,t;if(e=this.getExistingFallback())return e;var i='<div class="dz-fallback">';this.options.dictFallbackText&&(i+="<p>".concat(this.options.dictFallbackText,"</p>")),i+='<input type="file" name="'.concat(this._getParamName(0),'" ').concat(this.options.uploadMultiple?'multiple="multiple"':void 0,' /><input type="submit" value="Upload!"></div>');var n=o.createElement(i);return"FORM"!==this.element.tagName?(t=o.createElement('<form action="'.concat(this.options.url,'" enctype="multipart/form-data" method="').concat(this.options.method,'"></form>'))).appendChild(n):(this.element.setAttribute("enctype","multipart/form-data"),this.element.setAttribute("method",this.options.method)),null!=t?t:n}},{key:"getExistingFallback",value:function(){var e=function(e){var t=!0,i=!1,n=void 0;try{for(var r,a=e[Symbol.iterator]();!(t=(r=a.next()).done);t=!0){var o=r.value;if(/(^| )fallback($| )/.test(o.className))return o}}catch(e){i=!0,n=e}finally{try{t||null==a.return||a.return()}finally{if(i)throw n}}},t=!0,i=!1,n=void 0;try{for(var r,a=["div","form"][Symbol.iterator]();!(t=(r=a.next()).done);t=!0){var o,l=r.value;if(o=e(this.element.getElementsByTagName(l)))return o}}catch(e){i=!0,n=e}finally{try{t||null==a.return||a.return()}finally{if(i)throw n}}}},{key:"setupEventListeners",value:function(){return this.listeners.map((function(e){return function(){var t=[];for(var i in e.events){var n=e.events[i];t.push(e.element.addEventListener(i,n,!1))}return t}()}))}},{key:"removeEventListeners",value:function(){return this.listeners.map((function(e){return function(){var t=[];for(var i in e.events){var n=e.events[i];t.push(e.element.removeEventListener(i,n,!1))}return t}()}))}},{key:"disable",value:function(){var e=this;return this.clickableElements.forEach((function(e){return e.classList.remove("dz-clickable")})),this.removeEventListeners(),this.disabled=!0,this.files.map((function(t){return e.cancelUpload(t)}))}},{key:"enable",value:function(){return delete this.disabled,this.clickableElements.forEach((function(e){return e.classList.add("dz-clickable")})),this.setupEventListeners()}},{key:"filesize",value:function(e){var t=0,i="b";if(e>0){for(var n=["tb","gb","mb","kb","b"],r=0;r<n.length;r++){var a=n[r];if(e>=Math.pow(this.options.filesizeBase,4-r)/10){t=e/Math.pow(this.options.filesizeBase,4-r),i=a;break}}t=Math.round(10*t)/10}return"<strong>".concat(t,"</strong> ").concat(this.options.dictFileSizeUnits[i])}},{key:"_updateMaxFilesReachedClass",value:function(){return null!=this.options.maxFiles&&this.getAcceptedFiles().length>=this.options.maxFiles?(this.getAcceptedFiles().length===this.options.maxFiles&&this.emit("maxfilesreached",this.files),this.element.classList.add("dz-max-files-reached")):this.element.classList.remove("dz-max-files-reached")}},{key:"drop",value:function(e){if(e.dataTransfer){this.emit("drop",e);for(var t=[],i=0;i<e.dataTransfer.files.length;i++)t[i]=e.dataTransfer.files[i];if(t.length){var n=e.dataTransfer.items;n&&n.length&&null!=n[0].webkitGetAsEntry?this._addFilesFromItems(n):this.handleFiles(t)}this.emit("addedfiles",t)}}},{key:"paste",value:function(e){if(null!=(t=null!=e?e.clipboardData:void 0,i=function(e){return e.items},null!=t?i(t):void 0)){var t,i;this.emit("paste",e);var n=e.clipboardData.items;return n.length?this._addFilesFromItems(n):void 0}}},{key:"handleFiles",value:function(e){var t=!0,i=!1,n=void 0;try{for(var r,a=e[Symbol.iterator]();!(t=(r=a.next()).done);t=!0){var o=r.value;this.addFile(o)}}catch(e){i=!0,n=e}finally{try{t||null==a.return||a.return()}finally{if(i)throw n}}}},{key:"_addFilesFromItems",value:function(e){var t=this;return function(){var i=[],n=!0,r=!1,a=void 0;try{for(var o,l=e[Symbol.iterator]();!(n=(o=l.next()).done);n=!0){var s,u=o.value;null!=u.webkitGetAsEntry&&(s=u.webkitGetAsEntry())?s.isFile?i.push(t.addFile(u.getAsFile())):s.isDirectory?i.push(t._addFilesFromDirectory(s,s.name)):i.push(void 0):null!=u.getAsFile&&(null==u.kind||"file"===u.kind)?i.push(t.addFile(u.getAsFile())):i.push(void 0)}}catch(e){r=!0,a=e}finally{try{n||null==l.return||l.return()}finally{if(r)throw a}}return i}()}},{key:"_addFilesFromDirectory",value:function(e,t){var i=this,n=e.createReader(),r=function(e){return t=console,i="log",n=function(t){return t.log(e)},null!=t&&"function"==typeof t[i]?n(t,i):void 0;var t,i,n},a=function(){var e=i;return n.readEntries((function(i){if(i.length>0){var n=!0,r=!1,o=void 0;try{for(var l,s=i[Symbol.iterator]();!(n=(l=s.next()).done);n=!0){var u=l.value,c=e;u.isFile?u.file((function(e){if(!c.options.ignoreHiddenFiles||"."!==e.name.substring(0,1))return e.fullPath="".concat(t,"/").concat(e.name),c.addFile(e)})):u.isDirectory&&e._addFilesFromDirectory(u,"".concat(t,"/").concat(u.name))}}catch(e){r=!0,o=e}finally{try{n||null==s.return||s.return()}finally{if(r)throw o}}a()}return null}),r)};return a()}},{key:"accept",value:function(e,t){this.options.maxFilesize&&e.size>1048576*this.options.maxFilesize?t(this.options.dictFileTooBig.replace("{{filesize}}",Math.round(e.size/1024/10.24)/100).replace("{{maxFilesize}}",this.options.maxFilesize)):o.isValidFile(e,this.options.acceptedFiles)?null!=this.options.maxFiles&&this.getAcceptedFiles().length>=this.options.maxFiles?(t(this.options.dictMaxFilesExceeded.replace("{{maxFiles}}",this.options.maxFiles)),this.emit("maxfilesexceeded",e)):this.options.accept.call(this,e,t):t(this.options.dictInvalidFileType)}},{key:"addFile",value:function(e){var t=this;e.upload={uuid:o.uuidv4(),progress:0,total:e.size,bytesSent:0,filename:this._renameFile(e)},this.files.push(e),e.status=o.ADDED,this.emit("addedfile",e),this._enqueueThumbnail(e),this.accept(e,(function(i){i?(e.accepted=!1,t._errorProcessing([e],i)):(e.accepted=!0,t.options.autoQueue&&t.enqueueFile(e)),t._updateMaxFilesReachedClass()}))}},{key:"enqueueFiles",value:function(e){var t=!0,i=!1,n=void 0;try{for(var r,a=e[Symbol.iterator]();!(t=(r=a.next()).done);t=!0){var o=r.value;this.enqueueFile(o)}}catch(e){i=!0,n=e}finally{try{t||null==a.return||a.return()}finally{if(i)throw n}}return null}},{key:"enqueueFile",value:function(e){if(e.status!==o.ADDED||!0!==e.accepted)throw new Error("This file can't be queued because it has already been processed or was rejected.");var t=this;if(e.status=o.QUEUED,this.options.autoProcessQueue)return setTimeout((function(){return t.processQueue()}),0)}},{key:"_enqueueThumbnail",value:function(e){if(this.options.createImageThumbnails&&e.type.match(/image.*/)&&e.size<=1048576*this.options.maxThumbnailFilesize){var t=this;return this._thumbnailQueue.push(e),setTimeout((function(){return t._processThumbnailQueue()}),0)}}},{key:"_processThumbnailQueue",value:function(){var e=this;if(!this._processingThumbnail&&0!==this._thumbnailQueue.length){this._processingThumbnail=!0;var t=this._thumbnailQueue.shift();return this.createThumbnail(t,this.options.thumbnailWidth,this.options.thumbnailHeight,this.options.thumbnailMethod,!0,(function(i){return e.emit("thumbnail",t,i),e._processingThumbnail=!1,e._processThumbnailQueue()}))}}},{key:"removeFile",value:function(e){if(e.status===o.UPLOADING&&this.cancelUpload(e),this.files=m(this.files,e),this.emit("removedfile",e),0===this.files.length)return this.emit("reset")}},{key:"removeAllFiles",value:function(e){null==e&&(e=!1);var t=!0,i=!1,n=void 0;try{for(var r,a=this.files.slice()[Symbol.iterator]();!(t=(r=a.next()).done);t=!0){var l=r.value;(l.status!==o.UPLOADING||e)&&this.removeFile(l)}}catch(e){i=!0,n=e}finally{try{t||null==a.return||a.return()}finally{if(i)throw n}}return null}},{key:"resizeImage",value:function(e,t,i,n,r){var a=this;return this.createThumbnail(e,t,i,n,!0,(function(t,i){if(null==i)return r(e);var n=a.options.resizeMimeType;null==n&&(n=e.type);var l=i.toDataURL(n,a.options.resizeQuality);return"image/jpeg"!==n&&"image/jpg"!==n||(l=g.restore(e.dataURL,l)),r(o.dataURItoBlob(l))}))}},{key:"createThumbnail",value:function(e,t,i,n,r,a){var o=this,l=new FileReader;l.onload=function(){e.dataURL=l.result,"image/svg+xml"!==e.type?o.createThumbnailFromUrl(e,t,i,n,r,a):null!=a&&a(l.result)},l.readAsDataURL(e)}},{key:"displayExistingFile",value:function(e,t,i,n,r){var a=void 0===r||r;if(this.emit("addedfile",e),this.emit("complete",e),a){var o=this;e.dataURL=t,this.createThumbnailFromUrl(e,this.options.thumbnailWidth,this.options.thumbnailHeight,this.options.thumbnailMethod,this.options.fixOrientation,(function(t){o.emit("thumbnail",e,t),i&&i()}),n)}else this.emit("thumbnail",e,t),i&&i()}},{key:"createThumbnailFromUrl",value:function(e,t,i,n,r,a,o){var l=this,s=document.createElement("img");return o&&(s.crossOrigin=o),r="from-image"!=getComputedStyle(document.body).imageOrientation&&r,s.onload=function(){var o=l,u=function(e){return e(1)};return"undefined"!=typeof EXIF&&null!==EXIF&&r&&(u=function(e){return EXIF.getData(s,(function(){return e(EXIF.getTag(this,"Orientation"))}))}),u((function(r){e.width=s.width,e.height=s.height;var l=o.options.resize.call(o,e,t,i,n),u=document.createElement("canvas"),c=u.getContext("2d");switch(u.width=l.trgWidth,u.height=l.trgHeight,r>4&&(u.width=l.trgHeight,u.height=l.trgWidth),r){case 2:c.translate(u.width,0),c.scale(-1,1);break;case 3:c.translate(u.width,u.height),c.rotate(Math.PI);break;case 4:c.translate(0,u.height),c.scale(1,-1);break;case 5:c.rotate(.5*Math.PI),c.scale(1,-1);break;case 6:c.rotate(.5*Math.PI),c.translate(0,-u.width);break;case 7:c.rotate(.5*Math.PI),c.translate(u.height,-u.width),c.scale(-1,1);break;case 8:c.rotate(-.5*Math.PI),c.translate(-u.height,0)}y(c,s,null!=l.srcX?l.srcX:0,null!=l.srcY?l.srcY:0,l.srcWidth,l.srcHeight,null!=l.trgX?l.trgX:0,null!=l.trgY?l.trgY:0,l.trgWidth,l.trgHeight);var d=u.toDataURL("image/png");if(null!=a)return a(d,u)}))},null!=a&&(s.onerror=a),s.src=e.dataURL}},{key:"processQueue",value:function(){var e=this.options.parallelUploads,t=this.getUploadingFiles().length,i=t;if(!(t>=e)){var n=this.getQueuedFiles();if(n.length>0){if(this.options.uploadMultiple)return this.processFiles(n.slice(0,e-t));for(;i<e;){if(!n.length)return;this.processFile(n.shift()),i++}}}}},{key:"processFile",value:function(e){return this.processFiles([e])}},{key:"processFiles",value:function(e){var t=!0,i=!1,n=void 0;try{for(var r,a=e[Symbol.iterator]();!(t=(r=a.next()).done);t=!0){var l=r.value;l.processing=!0,l.status=o.UPLOADING,this.emit("processing",l)}}catch(e){i=!0,n=e}finally{try{t||null==a.return||a.return()}finally{if(i)throw n}}return this.options.uploadMultiple&&this.emit("processingmultiple",e),this.uploadFiles(e)}},{key:"_getFilesWithXhr",value:function(e){return this.files.filter((function(t){return t.xhr===e})).map((function(e){return e}))}},{key:"cancelUpload",value:function(e){if(e.status===o.UPLOADING){var t=this._getFilesWithXhr(e.xhr),i=!0,n=!1,r=void 0;try{for(var a,l=t[Symbol.iterator]();!(i=(a=l.next()).done);i=!0){(p=a.value).status=o.CANCELED}}catch(e){n=!0,r=e}finally{try{i||null==l.return||l.return()}finally{if(n)throw r}}void 0!==e.xhr&&e.xhr.abort();var s=!0,u=!1,c=void 0;try{for(var d,h=t[Symbol.iterator]();!(s=(d=h.next()).done);s=!0){var p=d.value;this.emit("canceled",p)}}catch(e){u=!0,c=e}finally{try{s||null==h.return||h.return()}finally{if(u)throw c}}this.options.uploadMultiple&&this.emit("canceledmultiple",t)}else e.status!==o.ADDED&&e.status!==o.QUEUED||(e.status=o.CANCELED,this.emit("canceled",e),this.options.uploadMultiple&&this.emit("canceledmultiple",[e]));if(this.options.autoProcessQueue)return this.processQueue()}},{key:"resolveOption",value:function(e){for(var t=arguments.length,i=new Array(t>1?t-1:0),n=1;n<t;n++)i[n-1]=arguments[n];return"function"==typeof e?e.apply(this,i):e}},{key:"uploadFile",value:function(e){return this.uploadFiles([e])}},{key:"uploadFiles",value:function(e){var t=this;this._transformFiles(e,(function(i){if(t.options.chunking){var n=i[0];e[0].upload.chunked=t.options.chunking&&(t.options.forceChunking||n.size>t.options.chunkSize),e[0].upload.totalChunkCount=Math.ceil(n.size/t.options.chunkSize)}if(e[0].upload.chunked){var r=t,a=t,l=e[0];n=i[0];l.upload.chunks=[];var s=function(){for(var t=0;void 0!==l.upload.chunks[t];)t++;if(!(t>=l.upload.totalChunkCount)){0;var i=t*r.options.chunkSize,a=Math.min(i+r.options.chunkSize,n.size),s={name:r._getParamName(0),data:n.webkitSlice?n.webkitSlice(i,a):n.slice(i,a),filename:l.upload.filename,chunkIndex:t};l.upload.chunks[t]={file:l,index:t,dataBlock:s,status:o.UPLOADING,progress:0,retries:0},r._uploadData(e,[s])}};if(l.upload.finishedChunkUpload=function(t,i){var n=a,r=!0;t.status=o.SUCCESS,t.dataBlock=null,t.response=t.xhr.responseText,t.responseHeaders=t.xhr.getAllResponseHeaders(),t.xhr=null;for(var u=0;u<l.upload.totalChunkCount;u++){if(void 0===l.upload.chunks[u])return s();l.upload.chunks[u].status!==o.SUCCESS&&(r=!1)}r&&a.options.chunksUploaded(l,(function(){n._finished(e,i,null)}))},t.options.parallelChunkUploads)for(var u=0;u<l.upload.totalChunkCount;u++)s();else s()}else{var c=[];for(u=0;u<e.length;u++)c[u]={name:t._getParamName(u),data:i[u],filename:e[u].upload.filename};t._uploadData(e,c)}}))}},{key:"_getChunk",value:function(e,t){for(var i=0;i<e.upload.totalChunkCount;i++)if(void 0!==e.upload.chunks[i]&&e.upload.chunks[i].xhr===t)return e.upload.chunks[i]}},{key:"_uploadData",value:function(t,i){var n=this,r=this,a=this,o=this,l=new XMLHttpRequest,s=!0,c=!1,d=void 0;try{for(var h=t[Symbol.iterator]();!(s=(x=h.next()).done);s=!0){(g=x.value).xhr=l}}catch(e){c=!0,d=e}finally{try{s||null==h.return||h.return()}finally{if(c)throw d}}t[0].upload.chunked&&(t[0].upload.chunks[i[0].chunkIndex].xhr=l);var p=this.resolveOption(this.options.method,t,i),f=this.resolveOption(this.options.url,t,i);l.open(p,f,!0),this.resolveOption(this.options.timeout,t)&&(l.timeout=this.resolveOption(this.options.timeout,t)),l.withCredentials=!!this.options.withCredentials,l.onload=function(e){n._finishedUploading(t,l,e)},l.ontimeout=function(){r._handleUploadError(t,l,"Request timedout after ".concat(r.options.timeout/1e3," seconds"))},l.onerror=function(){a._handleUploadError(t,l)},(null!=l.upload?l.upload:l).onprogress=function(e){return o._updateFilesUploadProgress(t,l,e)};var m=this.options.defaultHeaders?{Accept:"application/json","Cache-Control":"no-cache","X-Requested-With":"XMLHttpRequest"}:{};for(var v in this.options.binaryBody&&(m["Content-Type"]=t[0].type),this.options.headers&&e(u)(m,this.options.headers),m){var y=m[v];y&&l.setRequestHeader(v,y)}if(this.options.binaryBody){s=!0,c=!1,d=void 0;try{for(h=t[Symbol.iterator]();!(s=(x=h.next()).done);s=!0){var g=x.value;this.emit("sending",g,l)}}catch(e){c=!0,d=e}finally{try{s||null==h.return||h.return()}finally{if(c)throw d}}this.options.uploadMultiple&&this.emit("sendingmultiple",t,l),this.submitRequest(l,null,t)}else{var b=new FormData;if(this.options.params){var k=this.options.params;for(var w in"function"==typeof k&&(k=k.call(this,t,l,t[0].upload.chunked?this._getChunk(t[0],l):null)),k){var F=k[w];if(Array.isArray(F))for(var E=0;E<F.length;E++)b.append(w,F[E]);else b.append(w,F)}}s=!0,c=!1,d=void 0;try{var x;for(h=t[Symbol.iterator]();!(s=(x=h.next()).done);s=!0){g=x.value;this.emit("sending",g,l,b)}}catch(e){c=!0,d=e}finally{try{s||null==h.return||h.return()}finally{if(c)throw d}}this.options.uploadMultiple&&this.emit("sendingmultiple",t,l,b),this._addFormElementData(b);for(E=0;E<i.length;E++){var z=i[E];b.append(z.name,z.data,z.filename)}this.submitRequest(l,b,t)}}},{key:"_transformFiles",value:function(e,t){for(var i=this,n=function(n){i.options.transformFile.call(i,e[n],(function(i){r[n]=i,++a===e.length&&t(r)}))},r=[],a=0,o=0;o<e.length;o++)n(o)}},{key:"_addFormElementData",value:function(e){var t=!0,i=!1,n=void 0;if("FORM"===this.element.tagName)try{for(var r=this.element.querySelectorAll("input, textarea, select, button")[Symbol.iterator]();!(t=(s=r.next()).done);t=!0){var a=s.value,o=a.getAttribute("name"),l=a.getAttribute("type");if(l&&(l=l.toLowerCase()),null!=o)if("SELECT"===a.tagName&&a.hasAttribute("multiple")){t=!0,i=!1,n=void 0;try{var s;for(r=a.options[Symbol.iterator]();!(t=(s=r.next()).done);t=!0){var u=s.value;u.selected&&e.append(o,u.value)}}catch(e){i=!0,n=e}finally{try{t||null==r.return||r.return()}finally{if(i)throw n}}}else(!l||"checkbox"!==l&&"radio"!==l||a.checked)&&e.append(o,a.value)}}catch(e){i=!0,n=e}finally{try{t||null==r.return||r.return()}finally{if(i)throw n}}}},{key:"_updateFilesUploadProgress",value:function(e,t,i){var n=!0,r=!1,a=void 0;if(e[0].upload.chunked){c=e[0];var o=this._getChunk(c,t);i?(o.progress=100*i.loaded/i.total,o.total=i.total,o.bytesSent=i.loaded):(o.progress=100,o.bytesSent=o.total),c.upload.progress=0,c.upload.total=0,c.upload.bytesSent=0;for(var l=0;l<c.upload.totalChunkCount;l++)c.upload.chunks[l]&&void 0!==c.upload.chunks[l].progress&&(c.upload.progress+=c.upload.chunks[l].progress,c.upload.total+=c.upload.chunks[l].total,c.upload.bytesSent+=c.upload.chunks[l].bytesSent);c.upload.progress=c.upload.progress/c.upload.totalChunkCount,this.emit("uploadprogress",c,c.upload.progress,c.upload.bytesSent)}else try{for(var s,u=e[Symbol.iterator]();!(n=(s=u.next()).done);n=!0){var c;(c=s.value).upload.total&&c.upload.bytesSent&&c.upload.bytesSent==c.upload.total||(i?(c.upload.progress=100*i.loaded/i.total,c.upload.total=i.total,c.upload.bytesSent=i.loaded):(c.upload.progress=100,c.upload.bytesSent=c.upload.total),this.emit("uploadprogress",c,c.upload.progress,c.upload.bytesSent))}}catch(e){r=!0,a=e}finally{try{n||null==u.return||u.return()}finally{if(r)throw a}}}},{key:"_finishedUploading",value:function(e,t,i){var n;if(e[0].status!==o.CANCELED&&4===t.readyState){if("arraybuffer"!==t.responseType&&"blob"!==t.responseType&&(n=t.responseText,t.getResponseHeader("content-type")&&~t.getResponseHeader("content-type").indexOf("application/json")))try{n=JSON.parse(n)}catch(e){i=e,n="Invalid JSON response from server."}this._updateFilesUploadProgress(e,t),200<=t.status&&t.status<300?e[0].upload.chunked?e[0].upload.finishedChunkUpload(this._getChunk(e[0],t),n):this._finished(e,n,i):this._handleUploadError(e,t,n)}}},{key:"_handleUploadError",value:function(e,t,i){if(e[0].status!==o.CANCELED){if(e[0].upload.chunked&&this.options.retryChunks){var n=this._getChunk(e[0],t);if(n.retries++<this.options.retryChunksLimit)return void this._uploadData(e,[n.dataBlock]);console.warn("Retried this chunk too often. Giving up.")}this._errorProcessing(e,i||this.options.dictResponseError.replace("{{statusCode}}",t.status),t)}}},{key:"submitRequest",value:function(e,t,i){if(1==e.readyState)if(this.options.binaryBody)if(i[0].upload.chunked){var n=this._getChunk(i[0],e);e.send(n.dataBlock.data)}else e.send(i[0]);else e.send(t);else console.warn("Cannot send this request because the XMLHttpRequest.readyState is not OPENED.")}},{key:"_finished",value:function(e,t,i){var n=!0,r=!1,a=void 0;try{for(var l,s=e[Symbol.iterator]();!(n=(l=s.next()).done);n=!0){var u=l.value;u.status=o.SUCCESS,this.emit("success",u,t,i),this.emit("complete",u)}}catch(e){r=!0,a=e}finally{try{n||null==s.return||s.return()}finally{if(r)throw a}}if(this.options.uploadMultiple&&(this.emit("successmultiple",e,t,i),this.emit("completemultiple",e)),this.options.autoProcessQueue)return this.processQueue()}},{key:"_errorProcessing",value:function(e,t,i){var n=!0,r=!1,a=void 0;try{for(var l,s=e[Symbol.iterator]();!(n=(l=s.next()).done);n=!0){var u=l.value;u.status=o.ERROR,this.emit("error",u,t,i),this.emit("complete",u)}}catch(e){r=!0,a=e}finally{try{n||null==s.return||s.return()}finally{if(r)throw a}}if(this.options.uploadMultiple&&(this.emit("errormultiple",e,t,i),this.emit("completemultiple",e)),this.options.autoProcessQueue)return this.processQueue()}}],[{key:"initClass",value:function(){this.prototype.Emitter=h,this.prototype.events=["drop","dragstart","dragend","dragenter","dragover","dragleave","addedfile","addedfiles","removedfile","thumbnail","error","errormultiple","processing","processingmultiple","uploadprogress","totaluploadprogress","sending","sendingmultiple","success","successmultiple","canceled","canceledmultiple","complete","completemultiple","reset","maxfilesexceeded","maxfilesreached","queuecomplete"],this.prototype._thumbnailQueue=[],this.prototype._processingThumbnail=!1}},{key:"uuidv4",value:function(){return"xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g,(function(e){var t=16*Math.random()|0;return("x"===e?t:3&t|8).toString(16)}))}}]),o}(h);f.initClass(),f.options={},f.optionsForElement=function(e){return e.getAttribute("id")?f.options[v(e.getAttribute("id"))]:void 0},f.instances=[],f.forElement=function(e){if("string"==typeof e&&(e=document.querySelector(e)),null==(null!=e?e.dropzone:void 0))throw new Error("No Dropzone found for given element. This is probably because you're trying to access it before Dropzone had the time to initialize. Use the `init` option to setup any additional observers on your Dropzone.");return e.dropzone},f.discover=function(){var e;if(document.querySelectorAll)e=document.querySelectorAll(".dropzone");else{e=[];var t=function(t){return function(){var i=[],n=!0,r=!1,a=void 0;try{for(var o,l=t[Symbol.iterator]();!(n=(o=l.next()).done);n=!0){var s=o.value;/(^| )dropzone($| )/.test(s.className)?i.push(e.push(s)):i.push(void 0)}}catch(e){r=!0,a=e}finally{try{n||null==l.return||l.return()}finally{if(r)throw a}}return i}()};t(document.getElementsByTagName("div")),t(document.getElementsByTagName("form"))}return function(){var t=[],i=!0,n=!1,r=void 0;try{for(var a,o=e[Symbol.iterator]();!(i=(a=o.next()).done);i=!0){var l=a.value;!1!==f.optionsForElement(l)?t.push(new f(l)):t.push(void 0)}}catch(e){n=!0,r=e}finally{try{i||null==o.return||o.return()}finally{if(n)throw r}}return t}()},f.blockedBrowsers=[/opera.*(Macintosh|Windows Phone).*version\/12/i],f.isBrowserSupported=function(){var e=!0;if(window.File&&window.FileReader&&window.FileList&&window.Blob&&window.FormData&&document.querySelector)if("classList"in document.createElement("a")){void 0!==f.blacklistedBrowsers&&(f.blockedBrowsers=f.blacklistedBrowsers);var t=!0,i=!1,n=void 0;try{for(var r,a=f.blockedBrowsers[Symbol.iterator]();!(t=(r=a.next()).done);t=!0){r.value.test(navigator.userAgent)&&(e=!1)}}catch(e){i=!0,n=e}finally{try{t||null==a.return||a.return()}finally{if(i)throw n}}}else e=!1;else e=!1;return e},f.dataURItoBlob=function(e){for(var t=atob(e.split(",")[1]),i=e.split(",")[0].split(":")[1].split(";")[0],n=new ArrayBuffer(t.length),r=new Uint8Array(n),a=0,o=t.length,l=0<=o;l?a<=o:a>=o;l?a++:a--)r[a]=t.charCodeAt(a);return new Blob([n],{type:i})};var m=function(e,t){return e.filter((function(e){return e!==t})).map((function(e){return e}))},v=function(e){return e.replace(/[\-_](\w)/g,(function(e){return e.charAt(1).toUpperCase()}))};f.createElement=function(e){var t=document.createElement("div");return t.innerHTML=e,t.childNodes[0]},f.elementInside=function(e,t){if(e===t)return!0;for(;e=e.parentNode;)if(e===t)return!0;return!1},f.getElement=function(e,t){var i;if("string"==typeof e?i=document.querySelector(e):null!=e.nodeType&&(i=e),null==i)throw new Error("Invalid `".concat(t,"` option provided. Please provide a CSS selector or a plain HTML element."));return i},f.getElements=function(e,t){var i,n;if(e instanceof Array){n=[];try{var r=!0,a=!1,o=void 0;try{for(var l=e[Symbol.iterator]();!(r=(s=l.next()).done);r=!0)i=s.value,n.push(this.getElement(i,t))}catch(e){a=!0,o=e}finally{try{r||null==l.return||l.return()}finally{if(a)throw o}}}catch(e){n=null}}else if("string"==typeof e){n=[];r=!0,a=!1,o=void 0;try{var s;for(l=document.querySelectorAll(e)[Symbol.iterator]();!(r=(s=l.next()).done);r=!0)i=s.value,n.push(i)}catch(e){a=!0,o=e}finally{try{r||null==l.return||l.return()}finally{if(a)throw o}}}else null!=e.nodeType&&(n=[e]);if(null==n||!n.length)throw new Error("Invalid `".concat(t,"` option provided. Please provide a CSS selector, a plain HTML element or a list of those."));return n},f.confirm=function(e,t,i){return window.confirm(e)?t():null!=i?i():void 0},f.isValidFile=function(e,t){if(!t)return!0;t=t.split(",");var i=e.type,n=i.replace(/\/.*$/,""),r=!0,a=!1,o=void 0;try{for(var l,s=t[Symbol.iterator]();!(r=(l=s.next()).done);r=!0){var u=l.value;if("."===(u=u.trim()).charAt(0)){if(-1!==e.name.toLowerCase().indexOf(u.toLowerCase(),e.name.length-u.length))return!0}else if(/\/\*$/.test(u)){if(n===u.replace(/\/.*$/,""))return!0}else if(i===u)return!0}}catch(e){a=!0,o=e}finally{try{r||null==s.return||s.return()}finally{if(a)throw o}}return!1},"undefined"!=typeof jQuery&&null!==jQuery&&(jQuery.fn.dropzone=function(e){return this.each((function(){return new f(this,e)}))}),f.ADDED="added",f.QUEUED="queued",f.ACCEPTED=f.QUEUED,f.UPLOADING="uploading",f.PROCESSING=f.UPLOADING,f.CANCELED="canceled",f.ERROR="error",f.SUCCESS="success";var y=function(e,t,i,n,r,a,o,l,s,u){var c=function(e){e.naturalWidth;var t=e.naturalHeight,i=document.createElement("canvas");i.width=1,i.height=t;var n=i.getContext("2d");n.drawImage(e,0,0);for(var r=n.getImageData(1,0,1,t).data,a=0,o=t,l=t;l>a;)0===r[4*(l-1)+3]?o=l:a=l,l=o+a>>1;var s=l/t;return 0===s?1:s}(t);return e.drawImage(t,i,n,r,a,o,l,s,u/c)},g=function(){"use strict";function e(){i(this,e)}return r(e,null,[{key:"initClass",value:function(){this.KEY_STR="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="}},{key:"encode64",value:function(e){for(var t="",i=void 0,n=void 0,r="",a=void 0,o=void 0,l=void 0,s="",u=0;a=(i=e[u++])>>2,o=(3&i)<<4|(n=e[u++])>>4,l=(15&n)<<2|(r=e[u++])>>6,s=63&r,isNaN(n)?l=s=64:isNaN(r)&&(s=64),t=t+this.KEY_STR.charAt(a)+this.KEY_STR.charAt(o)+this.KEY_STR.charAt(l)+this.KEY_STR.charAt(s),i=n=r="",a=o=l=s="",u<e.length;);return t}},{key:"restore",value:function(e,t){if(!e.match("data:image/jpeg;base64,"))return t;var i=this.decode64(e.replace("data:image/jpeg;base64,","")),n=this.slice2Segments(i),r=this.exifManipulation(t,n);return"data:image/jpeg;base64,".concat(this.encode64(r))}},{key:"exifManipulation",value:function(e,t){var i=this.getExifArray(t),n=this.insertExif(e,i);return new Uint8Array(n)}},{key:"getExifArray",value:function(e){for(var t=void 0,i=0;i<e.length;){if(255===(t=e[i])[0]&225===t[1])return t;i++}return[]}},{key:"insertExif",value:function(e,t){var i=e.replace("data:image/jpeg;base64,",""),n=this.decode64(i),r=n.indexOf(255,3),a=n.slice(0,r),o=n.slice(r),l=a;return l=(l=l.concat(t)).concat(o)}},{key:"slice2Segments",value:function(e){for(var t=0,i=[];;){if(255===e[t]&218===e[t+1])break;if(255===e[t]&216===e[t+1])t+=2;else{var n=t+(256*e[t+2]+e[t+3])+2,r=e.slice(t,n);i.push(r),t=n}if(t>e.length)break}return i}},{key:"decode64",value:function(e){var t=void 0,i=void 0,n="",r=void 0,a=void 0,o="",l=0,s=[];for(/[^A-Za-z0-9\+\/\=]/g.exec(e)&&console.warn("There were invalid base64 characters in the input text.\nValid base64 characters are A-Z, a-z, 0-9, '+', '/',and '='\nExpect errors in decoding."),e=e.replace(/[^A-Za-z0-9\+\/\=]/g,"");t=this.KEY_STR.indexOf(e.charAt(l++))<<2|(r=this.KEY_STR.indexOf(e.charAt(l++)))>>4,i=(15&r)<<4|(a=this.KEY_STR.indexOf(e.charAt(l++)))>>2,n=(3&a)<<6|(o=this.KEY_STR.indexOf(e.charAt(l++))),s.push(t),64!==a&&s.push(i),64!==o&&s.push(n),t=i=n="",r=a=o="",l<e.length;);return s}}]),e}();g.initClass();window.Dropzone=f}();


/* flatpickr v4.6.13,, @license MIT */
!function(e,n){"object"==typeof exports&&"undefined"!=typeof module?module.exports=n():"function"==typeof define&&define.amd?define(n):(e="undefined"!=typeof globalThis?globalThis:e||self).flatpickr=n()}(this,(function(){"use strict";var e=function(){return(e=Object.assign||function(e){for(var n,t=1,a=arguments.length;t<a;t++)for(var i in n=arguments[t])Object.prototype.hasOwnProperty.call(n,i)&&(e[i]=n[i]);return e}).apply(this,arguments)};function n(){for(var e=0,n=0,t=arguments.length;n<t;n++)e+=arguments[n].length;var a=Array(e),i=0;for(n=0;n<t;n++)for(var o=arguments[n],r=0,l=o.length;r<l;r++,i++)a[i]=o[r];return a}var t=["onChange","onClose","onDayCreate","onDestroy","onKeyDown","onMonthChange","onOpen","onParseConfig","onReady","onValueUpdate","onYearChange","onPreCalendarPosition"],a={_disable:[],allowInput:!1,allowInvalidPreload:!1,altFormat:"F j, Y",altInput:!1,altInputClass:"form-control input",animate:"object"==typeof window&&-1===window.navigator.userAgent.indexOf("MSIE"),ariaDateFormat:"F j, Y",autoFillDefaultTime:!0,clickOpens:!0,closeOnSelect:!0,conjunction:", ",dateFormat:"Y-m-d",defaultHour:12,defaultMinute:0,defaultSeconds:0,disable:[],disableMobile:!1,enableSeconds:!1,enableTime:!1,errorHandler:function(e){return"undefined"!=typeof console&&console.warn(e)},getWeek:function(e){var n=new Date(e.getTime());n.setHours(0,0,0,0),n.setDate(n.getDate()+3-(n.getDay()+6)%7);var t=new Date(n.getFullYear(),0,4);return 1+Math.round(((n.getTime()-t.getTime())/864e5-3+(t.getDay()+6)%7)/7)},hourIncrement:1,ignoredFocusElements:[],inline:!1,locale:"default",minuteIncrement:5,mode:"single",monthSelectorType:"dropdown",nextArrow:"<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 17 17'><g></g><path d='M13.207 8.472l-7.854 7.854-0.707-0.707 7.146-7.146-7.146-7.148 0.707-0.707 7.854 7.854z' /></svg>",noCalendar:!1,now:new Date,onChange:[],onClose:[],onDayCreate:[],onDestroy:[],onKeyDown:[],onMonthChange:[],onOpen:[],onParseConfig:[],onReady:[],onValueUpdate:[],onYearChange:[],onPreCalendarPosition:[],plugins:[],position:"auto",positionElement:void 0,prevArrow:"<svg version='1.1' xmlns='http://www.w3.org/2000/svg' xmlns:xlink='http://www.w3.org/1999/xlink' viewBox='0 0 17 17'><g></g><path d='M5.207 8.471l7.146 7.147-0.707 0.707-7.853-7.854 7.854-7.853 0.707 0.707-7.147 7.146z' /></svg>",shorthandCurrentMonth:!1,showMonths:1,static:!1,time_24hr:!1,weekNumbers:!1,wrap:!1},i={weekdays:{shorthand:["Sun","Mon","Tue","Wed","Thu","Fri","Sat"],longhand:["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]},months:{shorthand:["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],longhand:["January","February","March","April","May","June","July","August","September","October","November","December"]},daysInMonth:[31,28,31,30,31,30,31,31,30,31,30,31],firstDayOfWeek:0,ordinal:function(e){var n=e%100;if(n>3&&n<21)return"th";switch(n%10){case 1:return"st";case 2:return"nd";case 3:return"rd";default:return"th"}},rangeSeparator:" to ",weekAbbreviation:"Wk",scrollTitle:"Scroll to increment",toggleTitle:"Click to toggle",amPM:["AM","PM"],yearAriaLabel:"Year",monthAriaLabel:"Month",hourAriaLabel:"Hour",minuteAriaLabel:"Minute",time_24hr:!1},o=function(e,n){return void 0===n&&(n=2),("000"+e).slice(-1*n)},r=function(e){return!0===e?1:0};function l(e,n){var t;return function(){var a=this,i=arguments;clearTimeout(t),t=setTimeout((function(){return e.apply(a,i)}),n)}}var c=function(e){return e instanceof Array?e:[e]};function s(e,n,t){if(!0===t)return e.classList.add(n);e.classList.remove(n)}function d(e,n,t){var a=window.document.createElement(e);return n=n||"",t=t||"",a.className=n,void 0!==t&&(a.textContent=t),a}function u(e){for(;e.firstChild;)e.removeChild(e.firstChild)}function f(e,n){return n(e)?e:e.parentNode?f(e.parentNode,n):void 0}function m(e,n){var t=d("div","numInputWrapper"),a=d("input","numInput "+e),i=d("span","arrowUp"),o=d("span","arrowDown");if(-1===navigator.userAgent.indexOf("MSIE 9.0")?a.type="number":(a.type="text",a.pattern="\\d*"),void 0!==n)for(var r in n)a.setAttribute(r,n[r]);return t.appendChild(a),t.appendChild(i),t.appendChild(o),t}function g(e){try{return"function"==typeof e.composedPath?e.composedPath()[0]:e.target}catch(n){return e.target}}var p=function(){},h=function(e,n,t){return t.months[n?"shorthand":"longhand"][e]},v={D:p,F:function(e,n,t){e.setMonth(t.months.longhand.indexOf(n))},G:function(e,n){e.setHours((e.getHours()>=12?12:0)+parseFloat(n))},H:function(e,n){e.setHours(parseFloat(n))},J:function(e,n){e.setDate(parseFloat(n))},K:function(e,n,t){e.setHours(e.getHours()%12+12*r(new RegExp(t.amPM[1],"i").test(n)))},M:function(e,n,t){e.setMonth(t.months.shorthand.indexOf(n))},S:function(e,n){e.setSeconds(parseFloat(n))},U:function(e,n){return new Date(1e3*parseFloat(n))},W:function(e,n,t){var a=parseInt(n),i=new Date(e.getFullYear(),0,2+7*(a-1),0,0,0,0);return i.setDate(i.getDate()-i.getDay()+t.firstDayOfWeek),i},Y:function(e,n){e.setFullYear(parseFloat(n))},Z:function(e,n){return new Date(n)},d:function(e,n){e.setDate(parseFloat(n))},h:function(e,n){e.setHours((e.getHours()>=12?12:0)+parseFloat(n))},i:function(e,n){e.setMinutes(parseFloat(n))},j:function(e,n){e.setDate(parseFloat(n))},l:p,m:function(e,n){e.setMonth(parseFloat(n)-1)},n:function(e,n){e.setMonth(parseFloat(n)-1)},s:function(e,n){e.setSeconds(parseFloat(n))},u:function(e,n){return new Date(parseFloat(n))},w:p,y:function(e,n){e.setFullYear(2e3+parseFloat(n))}},D={D:"",F:"",G:"(\\d\\d|\\d)",H:"(\\d\\d|\\d)",J:"(\\d\\d|\\d)\\w+",K:"",M:"",S:"(\\d\\d|\\d)",U:"(.+)",W:"(\\d\\d|\\d)",Y:"(\\d{4})",Z:"(.+)",d:"(\\d\\d|\\d)",h:"(\\d\\d|\\d)",i:"(\\d\\d|\\d)",j:"(\\d\\d|\\d)",l:"",m:"(\\d\\d|\\d)",n:"(\\d\\d|\\d)",s:"(\\d\\d|\\d)",u:"(.+)",w:"(\\d\\d|\\d)",y:"(\\d{2})"},w={Z:function(e){return e.toISOString()},D:function(e,n,t){return n.weekdays.shorthand[w.w(e,n,t)]},F:function(e,n,t){return h(w.n(e,n,t)-1,!1,n)},G:function(e,n,t){return o(w.h(e,n,t))},H:function(e){return o(e.getHours())},J:function(e,n){return void 0!==n.ordinal?e.getDate()+n.ordinal(e.getDate()):e.getDate()},K:function(e,n){return n.amPM[r(e.getHours()>11)]},M:function(e,n){return h(e.getMonth(),!0,n)},S:function(e){return o(e.getSeconds())},U:function(e){return e.getTime()/1e3},W:function(e,n,t){return t.getWeek(e)},Y:function(e){return o(e.getFullYear(),4)},d:function(e){return o(e.getDate())},h:function(e){return e.getHours()%12?e.getHours()%12:12},i:function(e){return o(e.getMinutes())},j:function(e){return e.getDate()},l:function(e,n){return n.weekdays.longhand[e.getDay()]},m:function(e){return o(e.getMonth()+1)},n:function(e){return e.getMonth()+1},s:function(e){return e.getSeconds()},u:function(e){return e.getTime()},w:function(e){return e.getDay()},y:function(e){return String(e.getFullYear()).substring(2)}},b=function(e){var n=e.config,t=void 0===n?a:n,o=e.l10n,r=void 0===o?i:o,l=e.isMobile,c=void 0!==l&&l;return function(e,n,a){var i=a||r;return void 0===t.formatDate||c?n.split("").map((function(n,a,o){return w[n]&&"\\"!==o[a-1]?w[n](e,i,t):"\\"!==n?n:""})).join(""):t.formatDate(e,n,i)}},C=function(e){var n=e.config,t=void 0===n?a:n,o=e.l10n,r=void 0===o?i:o;return function(e,n,i,o){if(0===e||e){var l,c=o||r,s=e;if(e instanceof Date)l=new Date(e.getTime());else if("string"!=typeof e&&void 0!==e.toFixed)l=new Date(e);else if("string"==typeof e){var d=n||(t||a).dateFormat,u=String(e).trim();if("today"===u)l=new Date,i=!0;else if(t&&t.parseDate)l=t.parseDate(e,d);else if(/Z$/.test(u)||/GMT$/.test(u))l=new Date(e);else{for(var f=void 0,m=[],g=0,p=0,h="";g<d.length;g++){var w=d[g],b="\\"===w,C="\\"===d[g-1]||b;if(D[w]&&!C){h+=D[w];var M=new RegExp(h).exec(e);M&&(f=!0)&&m["Y"!==w?"push":"unshift"]({fn:v[w],val:M[++p]})}else b||(h+=".")}l=t&&t.noCalendar?new Date((new Date).setHours(0,0,0,0)):new Date((new Date).getFullYear(),0,1,0,0,0,0),m.forEach((function(e){var n=e.fn,t=e.val;return l=n(l,t,c)||l})),l=f?l:void 0}}if(l instanceof Date&&!isNaN(l.getTime()))return!0===i&&l.setHours(0,0,0,0),l;t.errorHandler(new Error("Invalid date provided: "+s))}}};function M(e,n,t){return void 0===t&&(t=!0),!1!==t?new Date(e.getTime()).setHours(0,0,0,0)-new Date(n.getTime()).setHours(0,0,0,0):e.getTime()-n.getTime()}var y=function(e,n,t){return 3600*e+60*n+t},x=864e5;function E(e){var n=e.defaultHour,t=e.defaultMinute,a=e.defaultSeconds;if(void 0!==e.minDate){var i=e.minDate.getHours(),o=e.minDate.getMinutes(),r=e.minDate.getSeconds();n<i&&(n=i),n===i&&t<o&&(t=o),n===i&&t===o&&a<r&&(a=e.minDate.getSeconds())}if(void 0!==e.maxDate){var l=e.maxDate.getHours(),c=e.maxDate.getMinutes();(n=Math.min(n,l))===l&&(t=Math.min(c,t)),n===l&&t===c&&(a=e.maxDate.getSeconds())}return{hours:n,minutes:t,seconds:a}}"function"!=typeof Object.assign&&(Object.assign=function(e){for(var n=[],t=1;t<arguments.length;t++)n[t-1]=arguments[t];if(!e)throw TypeError("Cannot convert undefined or null to object");for(var a=function(n){n&&Object.keys(n).forEach((function(t){return e[t]=n[t]}))},i=0,o=n;i<o.length;i++){var r=o[i];a(r)}return e});function k(p,v){var w={config:e(e({},a),I.defaultConfig),l10n:i};function k(){var e;return(null===(e=w.calendarContainer)||void 0===e?void 0:e.getRootNode()).activeElement||document.activeElement}function T(e){return e.bind(w)}function S(){var e=w.config;!1===e.weekNumbers&&1===e.showMonths||!0!==e.noCalendar&&window.requestAnimationFrame((function(){if(void 0!==w.calendarContainer&&(w.calendarContainer.style.visibility="hidden",w.calendarContainer.style.display="block"),void 0!==w.daysContainer){var n=(w.days.offsetWidth+1)*e.showMonths;w.daysContainer.style.width=n+"px",w.calendarContainer.style.width=n+(void 0!==w.weekWrapper?w.weekWrapper.offsetWidth:0)+"px",w.calendarContainer.style.removeProperty("visibility"),w.calendarContainer.style.removeProperty("display")}}))}function _(e){if(0===w.selectedDates.length){var n=void 0===w.config.minDate||M(new Date,w.config.minDate)>=0?new Date:new Date(w.config.minDate.getTime()),t=E(w.config);n.setHours(t.hours,t.minutes,t.seconds,n.getMilliseconds()),w.selectedDates=[n],w.latestSelectedDateObj=n}void 0!==e&&"blur"!==e.type&&function(e){e.preventDefault();var n="keydown"===e.type,t=g(e),a=t;void 0!==w.amPM&&t===w.amPM&&(w.amPM.textContent=w.l10n.amPM[r(w.amPM.textContent===w.l10n.amPM[0])]);var i=parseFloat(a.getAttribute("min")),l=parseFloat(a.getAttribute("max")),c=parseFloat(a.getAttribute("step")),s=parseInt(a.value,10),d=e.delta||(n?38===e.which?1:-1:0),u=s+c*d;if(void 0!==a.value&&2===a.value.length){var f=a===w.hourElement,m=a===w.minuteElement;u<i?(u=l+u+r(!f)+(r(f)&&r(!w.amPM)),m&&L(void 0,-1,w.hourElement)):u>l&&(u=a===w.hourElement?u-l-r(!w.amPM):i,m&&L(void 0,1,w.hourElement)),w.amPM&&f&&(1===c?u+s===23:Math.abs(u-s)>c)&&(w.amPM.textContent=w.l10n.amPM[r(w.amPM.textContent===w.l10n.amPM[0])]),a.value=o(u)}}(e);var a=w._input.value;O(),ye(),w._input.value!==a&&w._debouncedChange()}function O(){if(void 0!==w.hourElement&&void 0!==w.minuteElement){var e,n,t=(parseInt(w.hourElement.value.slice(-2),10)||0)%24,a=(parseInt(w.minuteElement.value,10)||0)%60,i=void 0!==w.secondElement?(parseInt(w.secondElement.value,10)||0)%60:0;void 0!==w.amPM&&(e=t,n=w.amPM.textContent,t=e%12+12*r(n===w.l10n.amPM[1]));var o=void 0!==w.config.minTime||w.config.minDate&&w.minDateHasTime&&w.latestSelectedDateObj&&0===M(w.latestSelectedDateObj,w.config.minDate,!0),l=void 0!==w.config.maxTime||w.config.maxDate&&w.maxDateHasTime&&w.latestSelectedDateObj&&0===M(w.latestSelectedDateObj,w.config.maxDate,!0);if(void 0!==w.config.maxTime&&void 0!==w.config.minTime&&w.config.minTime>w.config.maxTime){var c=y(w.config.minTime.getHours(),w.config.minTime.getMinutes(),w.config.minTime.getSeconds()),s=y(w.config.maxTime.getHours(),w.config.maxTime.getMinutes(),w.config.maxTime.getSeconds()),d=y(t,a,i);if(d>s&&d<c){var u=function(e){var n=Math.floor(e/3600),t=(e-3600*n)/60;return[n,t,e-3600*n-60*t]}(c);t=u[0],a=u[1],i=u[2]}}else{if(l){var f=void 0!==w.config.maxTime?w.config.maxTime:w.config.maxDate;(t=Math.min(t,f.getHours()))===f.getHours()&&(a=Math.min(a,f.getMinutes())),a===f.getMinutes()&&(i=Math.min(i,f.getSeconds()))}if(o){var m=void 0!==w.config.minTime?w.config.minTime:w.config.minDate;(t=Math.max(t,m.getHours()))===m.getHours()&&a<m.getMinutes()&&(a=m.getMinutes()),a===m.getMinutes()&&(i=Math.max(i,m.getSeconds()))}}A(t,a,i)}}function F(e){var n=e||w.latestSelectedDateObj;n&&n instanceof Date&&A(n.getHours(),n.getMinutes(),n.getSeconds())}function A(e,n,t){void 0!==w.latestSelectedDateObj&&w.latestSelectedDateObj.setHours(e%24,n,t||0,0),w.hourElement&&w.minuteElement&&!w.isMobile&&(w.hourElement.value=o(w.config.time_24hr?e:(12+e)%12+12*r(e%12==0)),w.minuteElement.value=o(n),void 0!==w.amPM&&(w.amPM.textContent=w.l10n.amPM[r(e>=12)]),void 0!==w.secondElement&&(w.secondElement.value=o(t)))}function N(e){var n=g(e),t=parseInt(n.value)+(e.delta||0);(t/1e3>1||"Enter"===e.key&&!/[^\d]/.test(t.toString()))&&ee(t)}function P(e,n,t,a){return n instanceof Array?n.forEach((function(n){return P(e,n,t,a)})):e instanceof Array?e.forEach((function(e){return P(e,n,t,a)})):(e.addEventListener(n,t,a),void w._handlers.push({remove:function(){return e.removeEventListener(n,t,a)}}))}function Y(){De("onChange")}function j(e,n){var t=void 0!==e?w.parseDate(e):w.latestSelectedDateObj||(w.config.minDate&&w.config.minDate>w.now?w.config.minDate:w.config.maxDate&&w.config.maxDate<w.now?w.config.maxDate:w.now),a=w.currentYear,i=w.currentMonth;try{void 0!==t&&(w.currentYear=t.getFullYear(),w.currentMonth=t.getMonth())}catch(e){e.message="Invalid date supplied: "+t,w.config.errorHandler(e)}n&&w.currentYear!==a&&(De("onYearChange"),q()),!n||w.currentYear===a&&w.currentMonth===i||De("onMonthChange"),w.redraw()}function H(e){var n=g(e);~n.className.indexOf("arrow")&&L(e,n.classList.contains("arrowUp")?1:-1)}function L(e,n,t){var a=e&&g(e),i=t||a&&a.parentNode&&a.parentNode.firstChild,o=we("increment");o.delta=n,i&&i.dispatchEvent(o)}function R(e,n,t,a){var i=ne(n,!0),o=d("span",e,n.getDate().toString());return o.dateObj=n,o.$i=a,o.setAttribute("aria-label",w.formatDate(n,w.config.ariaDateFormat)),-1===e.indexOf("hidden")&&0===M(n,w.now)&&(w.todayDateElem=o,o.classList.add("today"),o.setAttribute("aria-current","date")),i?(o.tabIndex=-1,be(n)&&(o.classList.add("selected"),w.selectedDateElem=o,"range"===w.config.mode&&(s(o,"startRange",w.selectedDates[0]&&0===M(n,w.selectedDates[0],!0)),s(o,"endRange",w.selectedDates[1]&&0===M(n,w.selectedDates[1],!0)),"nextMonthDay"===e&&o.classList.add("inRange")))):o.classList.add("flatpickr-disabled"),"range"===w.config.mode&&function(e){return!("range"!==w.config.mode||w.selectedDates.length<2)&&(M(e,w.selectedDates[0])>=0&&M(e,w.selectedDates[1])<=0)}(n)&&!be(n)&&o.classList.add("inRange"),w.weekNumbers&&1===w.config.showMonths&&"prevMonthDay"!==e&&a%7==6&&w.weekNumbers.insertAdjacentHTML("beforeend","<span class='flatpickr-day'>"+w.config.getWeek(n)+"</span>"),De("onDayCreate",o),o}function W(e){e.focus(),"range"===w.config.mode&&oe(e)}function B(e){for(var n=e>0?0:w.config.showMonths-1,t=e>0?w.config.showMonths:-1,a=n;a!=t;a+=e)for(var i=w.daysContainer.children[a],o=e>0?0:i.children.length-1,r=e>0?i.children.length:-1,l=o;l!=r;l+=e){var c=i.children[l];if(-1===c.className.indexOf("hidden")&&ne(c.dateObj))return c}}function J(e,n){var t=k(),a=te(t||document.body),i=void 0!==e?e:a?t:void 0!==w.selectedDateElem&&te(w.selectedDateElem)?w.selectedDateElem:void 0!==w.todayDateElem&&te(w.todayDateElem)?w.todayDateElem:B(n>0?1:-1);void 0===i?w._input.focus():a?function(e,n){for(var t=-1===e.className.indexOf("Month")?e.dateObj.getMonth():w.currentMonth,a=n>0?w.config.showMonths:-1,i=n>0?1:-1,o=t-w.currentMonth;o!=a;o+=i)for(var r=w.daysContainer.children[o],l=t-w.currentMonth===o?e.$i+n:n<0?r.children.length-1:0,c=r.children.length,s=l;s>=0&&s<c&&s!=(n>0?c:-1);s+=i){var d=r.children[s];if(-1===d.className.indexOf("hidden")&&ne(d.dateObj)&&Math.abs(e.$i-s)>=Math.abs(n))return W(d)}w.changeMonth(i),J(B(i),0)}(i,n):W(i)}function K(e,n){for(var t=(new Date(e,n,1).getDay()-w.l10n.firstDayOfWeek+7)%7,a=w.utils.getDaysInMonth((n-1+12)%12,e),i=w.utils.getDaysInMonth(n,e),o=window.document.createDocumentFragment(),r=w.config.showMonths>1,l=r?"prevMonthDay hidden":"prevMonthDay",c=r?"nextMonthDay hidden":"nextMonthDay",s=a+1-t,u=0;s<=a;s++,u++)o.appendChild(R("flatpickr-day "+l,new Date(e,n-1,s),0,u));for(s=1;s<=i;s++,u++)o.appendChild(R("flatpickr-day",new Date(e,n,s),0,u));for(var f=i+1;f<=42-t&&(1===w.config.showMonths||u%7!=0);f++,u++)o.appendChild(R("flatpickr-day "+c,new Date(e,n+1,f%i),0,u));var m=d("div","dayContainer");return m.appendChild(o),m}function U(){if(void 0!==w.daysContainer){u(w.daysContainer),w.weekNumbers&&u(w.weekNumbers);for(var e=document.createDocumentFragment(),n=0;n<w.config.showMonths;n++){var t=new Date(w.currentYear,w.currentMonth,1);t.setMonth(w.currentMonth+n),e.appendChild(K(t.getFullYear(),t.getMonth()))}w.daysContainer.appendChild(e),w.days=w.daysContainer.firstChild,"range"===w.config.mode&&1===w.selectedDates.length&&oe()}}function q(){if(!(w.config.showMonths>1||"dropdown"!==w.config.monthSelectorType)){var e=function(e){return!(void 0!==w.config.minDate&&w.currentYear===w.config.minDate.getFullYear()&&e<w.config.minDate.getMonth())&&!(void 0!==w.config.maxDate&&w.currentYear===w.config.maxDate.getFullYear()&&e>w.config.maxDate.getMonth())};w.monthsDropdownContainer.tabIndex=-1,w.monthsDropdownContainer.innerHTML="";for(var n=0;n<12;n++)if(e(n)){var t=d("option","flatpickr-monthDropdown-month");t.value=new Date(w.currentYear,n).getMonth().toString(),t.textContent=h(n,w.config.shorthandCurrentMonth,w.l10n),t.tabIndex=-1,w.currentMonth===n&&(t.selected=!0),w.monthsDropdownContainer.appendChild(t)}}}function $(){var e,n=d("div","flatpickr-month"),t=window.document.createDocumentFragment();w.config.showMonths>1||"static"===w.config.monthSelectorType?e=d("span","cur-month"):(w.monthsDropdownContainer=d("select","flatpickr-monthDropdown-months"),w.monthsDropdownContainer.setAttribute("aria-label",w.l10n.monthAriaLabel),P(w.monthsDropdownContainer,"change",(function(e){var n=g(e),t=parseInt(n.value,10);w.changeMonth(t-w.currentMonth),De("onMonthChange")})),q(),e=w.monthsDropdownContainer);var a=m("cur-year",{tabindex:"-1"}),i=a.getElementsByTagName("input")[0];i.setAttribute("aria-label",w.l10n.yearAriaLabel),w.config.minDate&&i.setAttribute("min",w.config.minDate.getFullYear().toString()),w.config.maxDate&&(i.setAttribute("max",w.config.maxDate.getFullYear().toString()),i.disabled=!!w.config.minDate&&w.config.minDate.getFullYear()===w.config.maxDate.getFullYear());var o=d("div","flatpickr-current-month");return o.appendChild(e),o.appendChild(a),t.appendChild(o),n.appendChild(t),{container:n,yearElement:i,monthElement:e}}function V(){u(w.monthNav),w.monthNav.appendChild(w.prevMonthNav),w.config.showMonths&&(w.yearElements=[],w.monthElements=[]);for(var e=w.config.showMonths;e--;){var n=$();w.yearElements.push(n.yearElement),w.monthElements.push(n.monthElement),w.monthNav.appendChild(n.container)}w.monthNav.appendChild(w.nextMonthNav)}function z(){w.weekdayContainer?u(w.weekdayContainer):w.weekdayContainer=d("div","flatpickr-weekdays");for(var e=w.config.showMonths;e--;){var n=d("div","flatpickr-weekdaycontainer");w.weekdayContainer.appendChild(n)}return G(),w.weekdayContainer}function G(){if(w.weekdayContainer){var e=w.l10n.firstDayOfWeek,t=n(w.l10n.weekdays.shorthand);e>0&&e<t.length&&(t=n(t.splice(e,t.length),t.splice(0,e)));for(var a=w.config.showMonths;a--;)w.weekdayContainer.children[a].innerHTML="\n      <span class='flatpickr-weekday'>\n        "+t.join("</span><span class='flatpickr-weekday'>")+"\n      </span>\n      "}}function Z(e,n){void 0===n&&(n=!0);var t=n?e:e-w.currentMonth;t<0&&!0===w._hidePrevMonthArrow||t>0&&!0===w._hideNextMonthArrow||(w.currentMonth+=t,(w.currentMonth<0||w.currentMonth>11)&&(w.currentYear+=w.currentMonth>11?1:-1,w.currentMonth=(w.currentMonth+12)%12,De("onYearChange"),q()),U(),De("onMonthChange"),Ce())}function Q(e){return w.calendarContainer.contains(e)}function X(e){if(w.isOpen&&!w.config.inline){var n=g(e),t=Q(n),a=!(n===w.input||n===w.altInput||w.element.contains(n)||e.path&&e.path.indexOf&&(~e.path.indexOf(w.input)||~e.path.indexOf(w.altInput)))&&!t&&!Q(e.relatedTarget),i=!w.config.ignoredFocusElements.some((function(e){return e.contains(n)}));a&&i&&(w.config.allowInput&&w.setDate(w._input.value,!1,w.config.altInput?w.config.altFormat:w.config.dateFormat),void 0!==w.timeContainer&&void 0!==w.minuteElement&&void 0!==w.hourElement&&""!==w.input.value&&void 0!==w.input.value&&_(),w.close(),w.config&&"range"===w.config.mode&&1===w.selectedDates.length&&w.clear(!1))}}function ee(e){if(!(!e||w.config.minDate&&e<w.config.minDate.getFullYear()||w.config.maxDate&&e>w.config.maxDate.getFullYear())){var n=e,t=w.currentYear!==n;w.currentYear=n||w.currentYear,w.config.maxDate&&w.currentYear===w.config.maxDate.getFullYear()?w.currentMonth=Math.min(w.config.maxDate.getMonth(),w.currentMonth):w.config.minDate&&w.currentYear===w.config.minDate.getFullYear()&&(w.currentMonth=Math.max(w.config.minDate.getMonth(),w.currentMonth)),t&&(w.redraw(),De("onYearChange"),q())}}function ne(e,n){var t;void 0===n&&(n=!0);var a=w.parseDate(e,void 0,n);if(w.config.minDate&&a&&M(a,w.config.minDate,void 0!==n?n:!w.minDateHasTime)<0||w.config.maxDate&&a&&M(a,w.config.maxDate,void 0!==n?n:!w.maxDateHasTime)>0)return!1;if(!w.config.enable&&0===w.config.disable.length)return!0;if(void 0===a)return!1;for(var i=!!w.config.enable,o=null!==(t=w.config.enable)&&void 0!==t?t:w.config.disable,r=0,l=void 0;r<o.length;r++){if("function"==typeof(l=o[r])&&l(a))return i;if(l instanceof Date&&void 0!==a&&l.getTime()===a.getTime())return i;if("string"==typeof l){var c=w.parseDate(l,void 0,!0);return c&&c.getTime()===a.getTime()?i:!i}if("object"==typeof l&&void 0!==a&&l.from&&l.to&&a.getTime()>=l.from.getTime()&&a.getTime()<=l.to.getTime())return i}return!i}function te(e){return void 0!==w.daysContainer&&(-1===e.className.indexOf("hidden")&&-1===e.className.indexOf("flatpickr-disabled")&&w.daysContainer.contains(e))}function ae(e){var n=e.target===w._input,t=w._input.value.trimEnd()!==Me();!n||!t||e.relatedTarget&&Q(e.relatedTarget)||w.setDate(w._input.value,!0,e.target===w.altInput?w.config.altFormat:w.config.dateFormat)}function ie(e){var n=g(e),t=w.config.wrap?p.contains(n):n===w._input,a=w.config.allowInput,i=w.isOpen&&(!a||!t),o=w.config.inline&&t&&!a;if(13===e.keyCode&&t){if(a)return w.setDate(w._input.value,!0,n===w.altInput?w.config.altFormat:w.config.dateFormat),w.close(),n.blur();w.open()}else if(Q(n)||i||o){var r=!!w.timeContainer&&w.timeContainer.contains(n);switch(e.keyCode){case 13:r?(e.preventDefault(),_(),fe()):me(e);break;case 27:e.preventDefault(),fe();break;case 8:case 46:t&&!w.config.allowInput&&(e.preventDefault(),w.clear());break;case 37:case 39:if(r||t)w.hourElement&&w.hourElement.focus();else{e.preventDefault();var l=k();if(void 0!==w.daysContainer&&(!1===a||l&&te(l))){var c=39===e.keyCode?1:-1;e.ctrlKey?(e.stopPropagation(),Z(c),J(B(1),0)):J(void 0,c)}}break;case 38:case 40:e.preventDefault();var s=40===e.keyCode?1:-1;w.daysContainer&&void 0!==n.$i||n===w.input||n===w.altInput?e.ctrlKey?(e.stopPropagation(),ee(w.currentYear-s),J(B(1),0)):r||J(void 0,7*s):n===w.currentYearElement?ee(w.currentYear-s):w.config.enableTime&&(!r&&w.hourElement&&w.hourElement.focus(),_(e),w._debouncedChange());break;case 9:if(r){var d=[w.hourElement,w.minuteElement,w.secondElement,w.amPM].concat(w.pluginElements).filter((function(e){return e})),u=d.indexOf(n);if(-1!==u){var f=d[u+(e.shiftKey?-1:1)];e.preventDefault(),(f||w._input).focus()}}else!w.config.noCalendar&&w.daysContainer&&w.daysContainer.contains(n)&&e.shiftKey&&(e.preventDefault(),w._input.focus())}}if(void 0!==w.amPM&&n===w.amPM)switch(e.key){case w.l10n.amPM[0].charAt(0):case w.l10n.amPM[0].charAt(0).toLowerCase():w.amPM.textContent=w.l10n.amPM[0],O(),ye();break;case w.l10n.amPM[1].charAt(0):case w.l10n.amPM[1].charAt(0).toLowerCase():w.amPM.textContent=w.l10n.amPM[1],O(),ye()}(t||Q(n))&&De("onKeyDown",e)}function oe(e,n){if(void 0===n&&(n="flatpickr-day"),1===w.selectedDates.length&&(!e||e.classList.contains(n)&&!e.classList.contains("flatpickr-disabled"))){for(var t=e?e.dateObj.getTime():w.days.firstElementChild.dateObj.getTime(),a=w.parseDate(w.selectedDates[0],void 0,!0).getTime(),i=Math.min(t,w.selectedDates[0].getTime()),o=Math.max(t,w.selectedDates[0].getTime()),r=!1,l=0,c=0,s=i;s<o;s+=x)ne(new Date(s),!0)||(r=r||s>i&&s<o,s<a&&(!l||s>l)?l=s:s>a&&(!c||s<c)&&(c=s));Array.from(w.rContainer.querySelectorAll("*:nth-child(-n+"+w.config.showMonths+") > ."+n)).forEach((function(n){var i,o,s,d=n.dateObj.getTime(),u=l>0&&d<l||c>0&&d>c;if(u)return n.classList.add("notAllowed"),void["inRange","startRange","endRange"].forEach((function(e){n.classList.remove(e)}));r&&!u||(["startRange","inRange","endRange","notAllowed"].forEach((function(e){n.classList.remove(e)})),void 0!==e&&(e.classList.add(t<=w.selectedDates[0].getTime()?"startRange":"endRange"),a<t&&d===a?n.classList.add("startRange"):a>t&&d===a&&n.classList.add("endRange"),d>=l&&(0===c||d<=c)&&(o=a,s=t,(i=d)>Math.min(o,s)&&i<Math.max(o,s))&&n.classList.add("inRange")))}))}}function re(){!w.isOpen||w.config.static||w.config.inline||de()}function le(e){return function(n){var t=w.config["_"+e+"Date"]=w.parseDate(n,w.config.dateFormat),a=w.config["_"+("min"===e?"max":"min")+"Date"];void 0!==t&&(w["min"===e?"minDateHasTime":"maxDateHasTime"]=t.getHours()>0||t.getMinutes()>0||t.getSeconds()>0),w.selectedDates&&(w.selectedDates=w.selectedDates.filter((function(e){return ne(e)})),w.selectedDates.length||"min"!==e||F(t),ye()),w.daysContainer&&(ue(),void 0!==t?w.currentYearElement[e]=t.getFullYear().toString():w.currentYearElement.removeAttribute(e),w.currentYearElement.disabled=!!a&&void 0!==t&&a.getFullYear()===t.getFullYear())}}function ce(){return w.config.wrap?p.querySelector("[data-input]"):p}function se(){"object"!=typeof w.config.locale&&void 0===I.l10ns[w.config.locale]&&w.config.errorHandler(new Error("flatpickr: invalid locale "+w.config.locale)),w.l10n=e(e({},I.l10ns.default),"object"==typeof w.config.locale?w.config.locale:"default"!==w.config.locale?I.l10ns[w.config.locale]:void 0),D.D="("+w.l10n.weekdays.shorthand.join("|")+")",D.l="("+w.l10n.weekdays.longhand.join("|")+")",D.M="("+w.l10n.months.shorthand.join("|")+")",D.F="("+w.l10n.months.longhand.join("|")+")",D.K="("+w.l10n.amPM[0]+"|"+w.l10n.amPM[1]+"|"+w.l10n.amPM[0].toLowerCase()+"|"+w.l10n.amPM[1].toLowerCase()+")",void 0===e(e({},v),JSON.parse(JSON.stringify(p.dataset||{}))).time_24hr&&void 0===I.defaultConfig.time_24hr&&(w.config.time_24hr=w.l10n.time_24hr),w.formatDate=b(w),w.parseDate=C({config:w.config,l10n:w.l10n})}function de(e){if("function"!=typeof w.config.position){if(void 0!==w.calendarContainer){De("onPreCalendarPosition");var n=e||w._positionElement,t=Array.prototype.reduce.call(w.calendarContainer.children,(function(e,n){return e+n.offsetHeight}),0),a=w.calendarContainer.offsetWidth,i=w.config.position.split(" "),o=i[0],r=i.length>1?i[1]:null,l=n.getBoundingClientRect(),c=window.innerHeight-l.bottom,d="above"===o||"below"!==o&&c<t&&l.top>t,u=window.pageYOffset+l.top+(d?-t-2:n.offsetHeight+2);if(s(w.calendarContainer,"arrowTop",!d),s(w.calendarContainer,"arrowBottom",d),!w.config.inline){var f=window.pageXOffset+l.left,m=!1,g=!1;"center"===r?(f-=(a-l.width)/2,m=!0):"right"===r&&(f-=a-l.width,g=!0),s(w.calendarContainer,"arrowLeft",!m&&!g),s(w.calendarContainer,"arrowCenter",m),s(w.calendarContainer,"arrowRight",g);var p=window.document.body.offsetWidth-(window.pageXOffset+l.right),h=f+a>window.document.body.offsetWidth,v=p+a>window.document.body.offsetWidth;if(s(w.calendarContainer,"rightMost",h),!w.config.static)if(w.calendarContainer.style.top=u+"px",h)if(v){var D=function(){for(var e=null,n=0;n<document.styleSheets.length;n++){var t=document.styleSheets[n];if(t.cssRules){try{t.cssRules}catch(e){continue}e=t;break}}return null!=e?e:(a=document.createElement("style"),document.head.appendChild(a),a.sheet);var a}();if(void 0===D)return;var b=window.document.body.offsetWidth,C=Math.max(0,b/2-a/2),M=D.cssRules.length,y="{left:"+l.left+"px;right:auto;}";s(w.calendarContainer,"rightMost",!1),s(w.calendarContainer,"centerMost",!0),D.insertRule(".flatpickr-calendar.centerMost:before,.flatpickr-calendar.centerMost:after"+y,M),w.calendarContainer.style.left=C+"px",w.calendarContainer.style.right="auto"}else w.calendarContainer.style.left="auto",w.calendarContainer.style.right=p+"px";else w.calendarContainer.style.left=f+"px",w.calendarContainer.style.right="auto"}}}else w.config.position(w,e)}function ue(){w.config.noCalendar||w.isMobile||(q(),Ce(),U())}function fe(){w._input.focus(),-1!==window.navigator.userAgent.indexOf("MSIE")||void 0!==navigator.msMaxTouchPoints?setTimeout(w.close,0):w.close()}function me(e){e.preventDefault(),e.stopPropagation();var n=f(g(e),(function(e){return e.classList&&e.classList.contains("flatpickr-day")&&!e.classList.contains("flatpickr-disabled")&&!e.classList.contains("notAllowed")}));if(void 0!==n){var t=n,a=w.latestSelectedDateObj=new Date(t.dateObj.getTime()),i=(a.getMonth()<w.currentMonth||a.getMonth()>w.currentMonth+w.config.showMonths-1)&&"range"!==w.config.mode;if(w.selectedDateElem=t,"single"===w.config.mode)w.selectedDates=[a];else if("multiple"===w.config.mode){var o=be(a);o?w.selectedDates.splice(parseInt(o),1):w.selectedDates.push(a)}else"range"===w.config.mode&&(2===w.selectedDates.length&&w.clear(!1,!1),w.latestSelectedDateObj=a,w.selectedDates.push(a),0!==M(a,w.selectedDates[0],!0)&&w.selectedDates.sort((function(e,n){return e.getTime()-n.getTime()})));if(O(),i){var r=w.currentYear!==a.getFullYear();w.currentYear=a.getFullYear(),w.currentMonth=a.getMonth(),r&&(De("onYearChange"),q()),De("onMonthChange")}if(Ce(),U(),ye(),i||"range"===w.config.mode||1!==w.config.showMonths?void 0!==w.selectedDateElem&&void 0===w.hourElement&&w.selectedDateElem&&w.selectedDateElem.focus():W(t),void 0!==w.hourElement&&void 0!==w.hourElement&&w.hourElement.focus(),w.config.closeOnSelect){var l="single"===w.config.mode&&!w.config.enableTime,c="range"===w.config.mode&&2===w.selectedDates.length&&!w.config.enableTime;(l||c)&&fe()}Y()}}w.parseDate=C({config:w.config,l10n:w.l10n}),w._handlers=[],w.pluginElements=[],w.loadedPlugins=[],w._bind=P,w._setHoursFromDate=F,w._positionCalendar=de,w.changeMonth=Z,w.changeYear=ee,w.clear=function(e,n){void 0===e&&(e=!0);void 0===n&&(n=!0);w.input.value="",void 0!==w.altInput&&(w.altInput.value="");void 0!==w.mobileInput&&(w.mobileInput.value="");w.selectedDates=[],w.latestSelectedDateObj=void 0,!0===n&&(w.currentYear=w._initialDate.getFullYear(),w.currentMonth=w._initialDate.getMonth());if(!0===w.config.enableTime){var t=E(w.config),a=t.hours,i=t.minutes,o=t.seconds;A(a,i,o)}w.redraw(),e&&De("onChange")},w.close=function(){w.isOpen=!1,w.isMobile||(void 0!==w.calendarContainer&&w.calendarContainer.classList.remove("open"),void 0!==w._input&&w._input.classList.remove("active"));De("onClose")},w.onMouseOver=oe,w._createElement=d,w.createDay=R,w.destroy=function(){void 0!==w.config&&De("onDestroy");for(var e=w._handlers.length;e--;)w._handlers[e].remove();if(w._handlers=[],w.mobileInput)w.mobileInput.parentNode&&w.mobileInput.parentNode.removeChild(w.mobileInput),w.mobileInput=void 0;else if(w.calendarContainer&&w.calendarContainer.parentNode)if(w.config.static&&w.calendarContainer.parentNode){var n=w.calendarContainer.parentNode;if(n.lastChild&&n.removeChild(n.lastChild),n.parentNode){for(;n.firstChild;)n.parentNode.insertBefore(n.firstChild,n);n.parentNode.removeChild(n)}}else w.calendarContainer.parentNode.removeChild(w.calendarContainer);w.altInput&&(w.input.type="text",w.altInput.parentNode&&w.altInput.parentNode.removeChild(w.altInput),delete w.altInput);w.input&&(w.input.type=w.input._type,w.input.classList.remove("flatpickr-input"),w.input.removeAttribute("readonly"));["_showTimeInput","latestSelectedDateObj","_hideNextMonthArrow","_hidePrevMonthArrow","__hideNextMonthArrow","__hidePrevMonthArrow","isMobile","isOpen","selectedDateElem","minDateHasTime","maxDateHasTime","days","daysContainer","_input","_positionElement","innerContainer","rContainer","monthNav","todayDateElem","calendarContainer","weekdayContainer","prevMonthNav","nextMonthNav","monthsDropdownContainer","currentMonthElement","currentYearElement","navigationCurrentMonth","selectedDateElem","config"].forEach((function(e){try{delete w[e]}catch(e){}}))},w.isEnabled=ne,w.jumpToDate=j,w.updateValue=ye,w.open=function(e,n){void 0===n&&(n=w._positionElement);if(!0===w.isMobile){if(e){e.preventDefault();var t=g(e);t&&t.blur()}return void 0!==w.mobileInput&&(w.mobileInput.focus(),w.mobileInput.click()),void De("onOpen")}if(w._input.disabled||w.config.inline)return;var a=w.isOpen;w.isOpen=!0,a||(w.calendarContainer.classList.add("open"),w._input.classList.add("active"),De("onOpen"),de(n));!0===w.config.enableTime&&!0===w.config.noCalendar&&(!1!==w.config.allowInput||void 0!==e&&w.timeContainer.contains(e.relatedTarget)||setTimeout((function(){return w.hourElement.select()}),50))},w.redraw=ue,w.set=function(e,n){if(null!==e&&"object"==typeof e)for(var a in Object.assign(w.config,e),e)void 0!==ge[a]&&ge[a].forEach((function(e){return e()}));else w.config[e]=n,void 0!==ge[e]?ge[e].forEach((function(e){return e()})):t.indexOf(e)>-1&&(w.config[e]=c(n));w.redraw(),ye(!0)},w.setDate=function(e,n,t){void 0===n&&(n=!1);void 0===t&&(t=w.config.dateFormat);if(0!==e&&!e||e instanceof Array&&0===e.length)return w.clear(n);pe(e,t),w.latestSelectedDateObj=w.selectedDates[w.selectedDates.length-1],w.redraw(),j(void 0,n),F(),0===w.selectedDates.length&&w.clear(!1);ye(n),n&&De("onChange")},w.toggle=function(e){if(!0===w.isOpen)return w.close();w.open(e)};var ge={locale:[se,G],showMonths:[V,S,z],minDate:[j],maxDate:[j],positionElement:[ve],clickOpens:[function(){!0===w.config.clickOpens?(P(w._input,"focus",w.open),P(w._input,"click",w.open)):(w._input.removeEventListener("focus",w.open),w._input.removeEventListener("click",w.open))}]};function pe(e,n){var t=[];if(e instanceof Array)t=e.map((function(e){return w.parseDate(e,n)}));else if(e instanceof Date||"number"==typeof e)t=[w.parseDate(e,n)];else if("string"==typeof e)switch(w.config.mode){case"single":case"time":t=[w.parseDate(e,n)];break;case"multiple":t=e.split(w.config.conjunction).map((function(e){return w.parseDate(e,n)}));break;case"range":t=e.split(w.l10n.rangeSeparator).map((function(e){return w.parseDate(e,n)}))}else w.config.errorHandler(new Error("Invalid date supplied: "+JSON.stringify(e)));w.selectedDates=w.config.allowInvalidPreload?t:t.filter((function(e){return e instanceof Date&&ne(e,!1)})),"range"===w.config.mode&&w.selectedDates.sort((function(e,n){return e.getTime()-n.getTime()}))}function he(e){return e.slice().map((function(e){return"string"==typeof e||"number"==typeof e||e instanceof Date?w.parseDate(e,void 0,!0):e&&"object"==typeof e&&e.from&&e.to?{from:w.parseDate(e.from,void 0),to:w.parseDate(e.to,void 0)}:e})).filter((function(e){return e}))}function ve(){w._positionElement=w.config.positionElement||w._input}function De(e,n){if(void 0!==w.config){var t=w.config[e];if(void 0!==t&&t.length>0)for(var a=0;t[a]&&a<t.length;a++)t[a](w.selectedDates,w.input.value,w,n);"onChange"===e&&(w.input.dispatchEvent(we("change")),w.input.dispatchEvent(we("input")))}}function we(e){var n=document.createEvent("Event");return n.initEvent(e,!0,!0),n}function be(e){for(var n=0;n<w.selectedDates.length;n++){var t=w.selectedDates[n];if(t instanceof Date&&0===M(t,e))return""+n}return!1}function Ce(){w.config.noCalendar||w.isMobile||!w.monthNav||(w.yearElements.forEach((function(e,n){var t=new Date(w.currentYear,w.currentMonth,1);t.setMonth(w.currentMonth+n),w.config.showMonths>1||"static"===w.config.monthSelectorType?w.monthElements[n].textContent=h(t.getMonth(),w.config.shorthandCurrentMonth,w.l10n)+" ":w.monthsDropdownContainer.value=t.getMonth().toString(),e.value=t.getFullYear().toString()})),w._hidePrevMonthArrow=void 0!==w.config.minDate&&(w.currentYear===w.config.minDate.getFullYear()?w.currentMonth<=w.config.minDate.getMonth():w.currentYear<w.config.minDate.getFullYear()),w._hideNextMonthArrow=void 0!==w.config.maxDate&&(w.currentYear===w.config.maxDate.getFullYear()?w.currentMonth+1>w.config.maxDate.getMonth():w.currentYear>w.config.maxDate.getFullYear()))}function Me(e){var n=e||(w.config.altInput?w.config.altFormat:w.config.dateFormat);return w.selectedDates.map((function(e){return w.formatDate(e,n)})).filter((function(e,n,t){return"range"!==w.config.mode||w.config.enableTime||t.indexOf(e)===n})).join("range"!==w.config.mode?w.config.conjunction:w.l10n.rangeSeparator)}function ye(e){void 0===e&&(e=!0),void 0!==w.mobileInput&&w.mobileFormatStr&&(w.mobileInput.value=void 0!==w.latestSelectedDateObj?w.formatDate(w.latestSelectedDateObj,w.mobileFormatStr):""),w.input.value=Me(w.config.dateFormat),void 0!==w.altInput&&(w.altInput.value=Me(w.config.altFormat)),!1!==e&&De("onValueUpdate")}function xe(e){var n=g(e),t=w.prevMonthNav.contains(n),a=w.nextMonthNav.contains(n);t||a?Z(t?-1:1):w.yearElements.indexOf(n)>=0?n.select():n.classList.contains("arrowUp")?w.changeYear(w.currentYear+1):n.classList.contains("arrowDown")&&w.changeYear(w.currentYear-1)}return function(){w.element=w.input=p,w.isOpen=!1,function(){var n=["wrap","weekNumbers","allowInput","allowInvalidPreload","clickOpens","time_24hr","enableTime","noCalendar","altInput","shorthandCurrentMonth","inline","static","enableSeconds","disableMobile"],i=e(e({},JSON.parse(JSON.stringify(p.dataset||{}))),v),o={};w.config.parseDate=i.parseDate,w.config.formatDate=i.formatDate,Object.defineProperty(w.config,"enable",{get:function(){return w.config._enable},set:function(e){w.config._enable=he(e)}}),Object.defineProperty(w.config,"disable",{get:function(){return w.config._disable},set:function(e){w.config._disable=he(e)}});var r="time"===i.mode;if(!i.dateFormat&&(i.enableTime||r)){var l=I.defaultConfig.dateFormat||a.dateFormat;o.dateFormat=i.noCalendar||r?"H:i"+(i.enableSeconds?":S":""):l+" H:i"+(i.enableSeconds?":S":"")}if(i.altInput&&(i.enableTime||r)&&!i.altFormat){var s=I.defaultConfig.altFormat||a.altFormat;o.altFormat=i.noCalendar||r?"h:i"+(i.enableSeconds?":S K":" K"):s+" h:i"+(i.enableSeconds?":S":"")+" K"}Object.defineProperty(w.config,"minDate",{get:function(){return w.config._minDate},set:le("min")}),Object.defineProperty(w.config,"maxDate",{get:function(){return w.config._maxDate},set:le("max")});var d=function(e){return function(n){w.config["min"===e?"_minTime":"_maxTime"]=w.parseDate(n,"H:i:S")}};Object.defineProperty(w.config,"minTime",{get:function(){return w.config._minTime},set:d("min")}),Object.defineProperty(w.config,"maxTime",{get:function(){return w.config._maxTime},set:d("max")}),"time"===i.mode&&(w.config.noCalendar=!0,w.config.enableTime=!0);Object.assign(w.config,o,i);for(var u=0;u<n.length;u++)w.config[n[u]]=!0===w.config[n[u]]||"true"===w.config[n[u]];t.filter((function(e){return void 0!==w.config[e]})).forEach((function(e){w.config[e]=c(w.config[e]||[]).map(T)})),w.isMobile=!w.config.disableMobile&&!w.config.inline&&"single"===w.config.mode&&!w.config.disable.length&&!w.config.enable&&!w.config.weekNumbers&&/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);for(u=0;u<w.config.plugins.length;u++){var f=w.config.plugins[u](w)||{};for(var m in f)t.indexOf(m)>-1?w.config[m]=c(f[m]).map(T).concat(w.config[m]):void 0===i[m]&&(w.config[m]=f[m])}i.altInputClass||(w.config.altInputClass=ce().className+" "+w.config.altInputClass);De("onParseConfig")}(),se(),function(){if(w.input=ce(),!w.input)return void w.config.errorHandler(new Error("Invalid input element specified"));w.input._type=w.input.type,w.input.type="text",w.input.classList.add("flatpickr-input"),w._input=w.input,w.config.altInput&&(w.altInput=d(w.input.nodeName,w.config.altInputClass),w._input=w.altInput,w.altInput.placeholder=w.input.placeholder,w.altInput.disabled=w.input.disabled,w.altInput.required=w.input.required,w.altInput.tabIndex=w.input.tabIndex,w.altInput.type="text",w.input.setAttribute("type","hidden"),!w.config.static&&w.input.parentNode&&w.input.parentNode.insertBefore(w.altInput,w.input.nextSibling));w.config.allowInput||w._input.setAttribute("readonly","readonly");ve()}(),function(){w.selectedDates=[],w.now=w.parseDate(w.config.now)||new Date;var e=w.config.defaultDate||("INPUT"!==w.input.nodeName&&"TEXTAREA"!==w.input.nodeName||!w.input.placeholder||w.input.value!==w.input.placeholder?w.input.value:null);e&&pe(e,w.config.dateFormat);w._initialDate=w.selectedDates.length>0?w.selectedDates[0]:w.config.minDate&&w.config.minDate.getTime()>w.now.getTime()?w.config.minDate:w.config.maxDate&&w.config.maxDate.getTime()<w.now.getTime()?w.config.maxDate:w.now,w.currentYear=w._initialDate.getFullYear(),w.currentMonth=w._initialDate.getMonth(),w.selectedDates.length>0&&(w.latestSelectedDateObj=w.selectedDates[0]);void 0!==w.config.minTime&&(w.config.minTime=w.parseDate(w.config.minTime,"H:i"));void 0!==w.config.maxTime&&(w.config.maxTime=w.parseDate(w.config.maxTime,"H:i"));w.minDateHasTime=!!w.config.minDate&&(w.config.minDate.getHours()>0||w.config.minDate.getMinutes()>0||w.config.minDate.getSeconds()>0),w.maxDateHasTime=!!w.config.maxDate&&(w.config.maxDate.getHours()>0||w.config.maxDate.getMinutes()>0||w.config.maxDate.getSeconds()>0)}(),w.utils={getDaysInMonth:function(e,n){return void 0===e&&(e=w.currentMonth),void 0===n&&(n=w.currentYear),1===e&&(n%4==0&&n%100!=0||n%400==0)?29:w.l10n.daysInMonth[e]}},w.isMobile||function(){var e=window.document.createDocumentFragment();if(w.calendarContainer=d("div","flatpickr-calendar"),w.calendarContainer.tabIndex=-1,!w.config.noCalendar){if(e.appendChild((w.monthNav=d("div","flatpickr-months"),w.yearElements=[],w.monthElements=[],w.prevMonthNav=d("span","flatpickr-prev-month"),w.prevMonthNav.innerHTML=w.config.prevArrow,w.nextMonthNav=d("span","flatpickr-next-month"),w.nextMonthNav.innerHTML=w.config.nextArrow,V(),Object.defineProperty(w,"_hidePrevMonthArrow",{get:function(){return w.__hidePrevMonthArrow},set:function(e){w.__hidePrevMonthArrow!==e&&(s(w.prevMonthNav,"flatpickr-disabled",e),w.__hidePrevMonthArrow=e)}}),Object.defineProperty(w,"_hideNextMonthArrow",{get:function(){return w.__hideNextMonthArrow},set:function(e){w.__hideNextMonthArrow!==e&&(s(w.nextMonthNav,"flatpickr-disabled",e),w.__hideNextMonthArrow=e)}}),w.currentYearElement=w.yearElements[0],Ce(),w.monthNav)),w.innerContainer=d("div","flatpickr-innerContainer"),w.config.weekNumbers){var n=function(){w.calendarContainer.classList.add("hasWeeks");var e=d("div","flatpickr-weekwrapper");e.appendChild(d("span","flatpickr-weekday",w.l10n.weekAbbreviation));var n=d("div","flatpickr-weeks");return e.appendChild(n),{weekWrapper:e,weekNumbers:n}}(),t=n.weekWrapper,a=n.weekNumbers;w.innerContainer.appendChild(t),w.weekNumbers=a,w.weekWrapper=t}w.rContainer=d("div","flatpickr-rContainer"),w.rContainer.appendChild(z()),w.daysContainer||(w.daysContainer=d("div","flatpickr-days"),w.daysContainer.tabIndex=-1),U(),w.rContainer.appendChild(w.daysContainer),w.innerContainer.appendChild(w.rContainer),e.appendChild(w.innerContainer)}w.config.enableTime&&e.appendChild(function(){w.calendarContainer.classList.add("hasTime"),w.config.noCalendar&&w.calendarContainer.classList.add("noCalendar");var e=E(w.config);w.timeContainer=d("div","flatpickr-time"),w.timeContainer.tabIndex=-1;var n=d("span","flatpickr-time-separator",":"),t=m("flatpickr-hour",{"aria-label":w.l10n.hourAriaLabel});w.hourElement=t.getElementsByTagName("input")[0];var a=m("flatpickr-minute",{"aria-label":w.l10n.minuteAriaLabel});w.minuteElement=a.getElementsByTagName("input")[0],w.hourElement.tabIndex=w.minuteElement.tabIndex=-1,w.hourElement.value=o(w.latestSelectedDateObj?w.latestSelectedDateObj.getHours():w.config.time_24hr?e.hours:function(e){switch(e%24){case 0:case 12:return 12;default:return e%12}}(e.hours)),w.minuteElement.value=o(w.latestSelectedDateObj?w.latestSelectedDateObj.getMinutes():e.minutes),w.hourElement.setAttribute("step",w.config.hourIncrement.toString()),w.minuteElement.setAttribute("step",w.config.minuteIncrement.toString()),w.hourElement.setAttribute("min",w.config.time_24hr?"0":"1"),w.hourElement.setAttribute("max",w.config.time_24hr?"23":"12"),w.hourElement.setAttribute("maxlength","2"),w.minuteElement.setAttribute("min","0"),w.minuteElement.setAttribute("max","59"),w.minuteElement.setAttribute("maxlength","2"),w.timeContainer.appendChild(t),w.timeContainer.appendChild(n),w.timeContainer.appendChild(a),w.config.time_24hr&&w.timeContainer.classList.add("time24hr");if(w.config.enableSeconds){w.timeContainer.classList.add("hasSeconds");var i=m("flatpickr-second");w.secondElement=i.getElementsByTagName("input")[0],w.secondElement.value=o(w.latestSelectedDateObj?w.latestSelectedDateObj.getSeconds():e.seconds),w.secondElement.setAttribute("step",w.minuteElement.getAttribute("step")),w.secondElement.setAttribute("min","0"),w.secondElement.setAttribute("max","59"),w.secondElement.setAttribute("maxlength","2"),w.timeContainer.appendChild(d("span","flatpickr-time-separator",":")),w.timeContainer.appendChild(i)}w.config.time_24hr||(w.amPM=d("span","flatpickr-am-pm",w.l10n.amPM[r((w.latestSelectedDateObj?w.hourElement.value:w.config.defaultHour)>11)]),w.amPM.title=w.l10n.toggleTitle,w.amPM.tabIndex=-1,w.timeContainer.appendChild(w.amPM));return w.timeContainer}());s(w.calendarContainer,"rangeMode","range"===w.config.mode),s(w.calendarContainer,"animate",!0===w.config.animate),s(w.calendarContainer,"multiMonth",w.config.showMonths>1),w.calendarContainer.appendChild(e);var i=void 0!==w.config.appendTo&&void 0!==w.config.appendTo.nodeType;if((w.config.inline||w.config.static)&&(w.calendarContainer.classList.add(w.config.inline?"inline":"static"),w.config.inline&&(!i&&w.element.parentNode?w.element.parentNode.insertBefore(w.calendarContainer,w._input.nextSibling):void 0!==w.config.appendTo&&w.config.appendTo.appendChild(w.calendarContainer)),w.config.static)){var l=d("div","flatpickr-wrapper");w.element.parentNode&&w.element.parentNode.insertBefore(l,w.element),l.appendChild(w.element),w.altInput&&l.appendChild(w.altInput),l.appendChild(w.calendarContainer)}w.config.static||w.config.inline||(void 0!==w.config.appendTo?w.config.appendTo:window.document.body).appendChild(w.calendarContainer)}(),function(){w.config.wrap&&["open","close","toggle","clear"].forEach((function(e){Array.prototype.forEach.call(w.element.querySelectorAll("[data-"+e+"]"),(function(n){return P(n,"click",w[e])}))}));if(w.isMobile)return void function(){var e=w.config.enableTime?w.config.noCalendar?"time":"datetime-local":"date";w.mobileInput=d("input",w.input.className+" flatpickr-mobile"),w.mobileInput.tabIndex=1,w.mobileInput.type=e,w.mobileInput.disabled=w.input.disabled,w.mobileInput.required=w.input.required,w.mobileInput.placeholder=w.input.placeholder,w.mobileFormatStr="datetime-local"===e?"Y-m-d\\TH:i:S":"date"===e?"Y-m-d":"H:i:S",w.selectedDates.length>0&&(w.mobileInput.defaultValue=w.mobileInput.value=w.formatDate(w.selectedDates[0],w.mobileFormatStr));w.config.minDate&&(w.mobileInput.min=w.formatDate(w.config.minDate,"Y-m-d"));w.config.maxDate&&(w.mobileInput.max=w.formatDate(w.config.maxDate,"Y-m-d"));w.input.getAttribute("step")&&(w.mobileInput.step=String(w.input.getAttribute("step")));w.input.type="hidden",void 0!==w.altInput&&(w.altInput.type="hidden");try{w.input.parentNode&&w.input.parentNode.insertBefore(w.mobileInput,w.input.nextSibling)}catch(e){}P(w.mobileInput,"change",(function(e){w.setDate(g(e).value,!1,w.mobileFormatStr),De("onChange"),De("onClose")}))}();var e=l(re,50);w._debouncedChange=l(Y,300),w.daysContainer&&!/iPhone|iPad|iPod/i.test(navigator.userAgent)&&P(w.daysContainer,"mouseover",(function(e){"range"===w.config.mode&&oe(g(e))}));P(w._input,"keydown",ie),void 0!==w.calendarContainer&&P(w.calendarContainer,"keydown",ie);w.config.inline||w.config.static||P(window,"resize",e);void 0!==window.ontouchstart?P(window.document,"touchstart",X):P(window.document,"mousedown",X);P(window.document,"focus",X,{capture:!0}),!0===w.config.clickOpens&&(P(w._input,"focus",w.open),P(w._input,"click",w.open));void 0!==w.daysContainer&&(P(w.monthNav,"click",xe),P(w.monthNav,["keyup","increment"],N),P(w.daysContainer,"click",me));if(void 0!==w.timeContainer&&void 0!==w.minuteElement&&void 0!==w.hourElement){var n=function(e){return g(e).select()};P(w.timeContainer,["increment"],_),P(w.timeContainer,"blur",_,{capture:!0}),P(w.timeContainer,"click",H),P([w.hourElement,w.minuteElement],["focus","click"],n),void 0!==w.secondElement&&P(w.secondElement,"focus",(function(){return w.secondElement&&w.secondElement.select()})),void 0!==w.amPM&&P(w.amPM,"click",(function(e){_(e)}))}w.config.allowInput&&P(w._input,"blur",ae)}(),(w.selectedDates.length||w.config.noCalendar)&&(w.config.enableTime&&F(w.config.noCalendar?w.latestSelectedDateObj:void 0),ye(!1)),S();var n=/^((?!chrome|android).)*safari/i.test(navigator.userAgent);!w.isMobile&&n&&de(),De("onReady")}(),w}function T(e,n){for(var t=Array.prototype.slice.call(e).filter((function(e){return e instanceof HTMLElement})),a=[],i=0;i<t.length;i++){var o=t[i];try{if(null!==o.getAttribute("data-fp-omit"))continue;void 0!==o._flatpickr&&(o._flatpickr.destroy(),o._flatpickr=void 0),o._flatpickr=k(o,n||{}),a.push(o._flatpickr)}catch(e){console.error(e)}}return 1===a.length?a[0]:a}"undefined"!=typeof HTMLElement&&"undefined"!=typeof HTMLCollection&&"undefined"!=typeof NodeList&&(HTMLCollection.prototype.flatpickr=NodeList.prototype.flatpickr=function(e){return T(this,e)},HTMLElement.prototype.flatpickr=function(e){return T([this],e)});var I=function(e,n){return"string"==typeof e?T(window.document.querySelectorAll(e),n):e instanceof Node?T([e],n):T(e,n)};return I.defaultConfig={},I.l10ns={en:e({},i),default:e({},i)},I.localize=function(n){I.l10ns.default=e(e({},I.l10ns.default),n)},I.setDefaults=function(n){I.defaultConfig=e(e({},I.defaultConfig),n)},I.parseDate=C({}),I.formatDate=b({}),I.compareDates=M,"undefined"!=typeof jQuery&&void 0!==jQuery.fn&&(jQuery.fn.flatpickr=function(e){return T(this,e)}),Date.prototype.fp_incr=function(e){return new Date(this.getFullYear(),this.getMonth(),this.getDate()+("string"==typeof e?parseInt(e,10):e))},"undefined"!=typeof window&&(window.flatpickr=I),I}));
function passwordStrengthMeter(a){function b(){let a=c();d(a)}function c(){let a=0,b=/(?=.*[a-z])/,c=/(?=.*[A-Z])/,d=/(?=.*[0-9])/,e=new RegExp("(?=.{"+j+",})");return i.match(b)&&++a,i.match(c)&&++a,i.match(d)&&++a,i.match(e)&&++a,0==a&&0<i.length&&++a,a}function d(a){1===a?(g.className="password-strength-meter-score psms-25",k&&(k.textContent=l[1]||"Too simple"),f.dispatchEvent(new Event("onScore1",{bubbles:!0}))):2===a?(g.className="password-strength-meter-score psms-50",k&&(k.textContent=l[2]||"Simple"),f.dispatchEvent(new Event("onScore2",{bubbles:!0}))):3===a?(g.className="password-strength-meter-score psms-75",k&&(k.textContent=l[3]||"That's OK"),f.dispatchEvent(new Event("onScore3",{bubbles:!0}))):4===a?(g.className="password-strength-meter-score psms-100",k&&(k.textContent=l[4]||"Great password!"),f.dispatchEvent(new Event("onScore4",{bubbles:!0}))):(g.className="password-strength-meter-score",k&&(k.textContent=l[0]||"No data"),f.dispatchEvent(new Event("onScore0",{bubbles:!0})))}const e=document.createElement("style");document.body.prepend(e),e.innerHTML=`
    ${a.containerElement} {
      height: ${a.height||4}px;
      background-color: #eee;
      position: relative;
      overflow: hidden;
      border-radius: ${a.borderRadius.toString()||2}px;
    }
    ${a.containerElement} .password-strength-meter-score {
      height: inherit;
      width: 0%;
      transition: .3s ease-in-out;
      background: ${a.colorScore1||"#ff7700"};
    }
    ${a.containerElement} .password-strength-meter-score.psms-25 {width: 25%; background: ${a.colorScore1||"#ff7700"};}
    ${a.containerElement} .password-strength-meter-score.psms-50 {width: 50%; background: ${a.colorScore2||"#ffff00"};}
    ${a.containerElement} .password-strength-meter-score.psms-75 {width: 75%; background: ${a.colorScore3||"#aeff00"};}
    ${a.containerElement} .password-strength-meter-score.psms-100 {width: 100%; background: ${a.colorScore4||"#00ff00"};}`;const f=document.getElementById(a.containerElement.slice(1));f.classList.add("password-strength-meter");let g=document.createElement("div");g.classList.add("password-strength-meter-score"),f.appendChild(g);const h=document.getElementById(a.passwordInput.slice(1));let i="";h.addEventListener("keyup",function(){i=this.value,b()});let j=a.pswMinLength||8,k=a.showMessage?document.getElementById(a.messageContainer.slice(1)):null,l=void 0===a.messagesList?["No data","Too simple","Simple","That's OK","Great password!"]:a.messagesList;return k&&(k.textContent=l[0]||"No data"),{containerElement:f,getScore:c}}