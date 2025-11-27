(function($){function gsapTextAnimate($scope){let elements=$scope.find('.text-animate');if(!elements.length)return;const applyEffects=(el)=>{let text=$(el).find('> .pxl-title-text, > .pxl-subtitle-text, > p, > .pxl-post-title');let splitType=$(el).attr('data-split-text');let elClass=$(el).attr('class');let attrs={type:splitType??'lines',linesClass:'line',wordsClass:'word',charsClass:'char',tag:'div',};if(splitType==='words'){attrs={...attrs,type:'words'}}else if(splitType==='chars'){attrs={...attrs,type:'words, chars',wordsClass:'word'}}
if(el.splitTextInstance){el.splitTextInstance.revert()}
$(el).css('visibility','visible');let splitText;if(!$(el).hasClass('text-splitted')){splitText=new SplitText(text[0],attrs);$(el).addClass('text-splitted');el.splitTextInstance=splitText}else{splitText=el.splitTextInstance}
let animateTarget=[];let stagger=0.015;if(splitType==='chars'){animateTarget=splitText.chars}else if(splitType==='words'){animateTarget=splitText.words;stagger=stagger*3}else{animateTarget=splitText.lines;stagger=stagger*5}
let gsapParams={x:0,y:0,opacity:1,rotation:0,rotateX:0,duration:0.5,delay:0,stagger:stagger,force3D:!0,scrollTrigger:{trigger:el,start:"top 85%",end:"top 45%",toggleActions:`play none none none`,scrub:!1,},}
if(elClass.includes('text-fade-in')){gsapParams.opacity=0;if(elClass.includes('text-fade-in-right'))
gsapParams.x=30;else if(elClass.includes('text-fade-in-left'))
gsapParams.x=-30;else if(elClass.includes('text-fade-in-up'))
gsapParams.y=30;else if(elClass.includes('text-fade-in-down'))
gsapParams.y=-30}else if(elClass.includes('text-explosion')){gsapParams.x=()=>gsap.utils.random(-1000,1000)
gsapParams.y=()=>gsap.utils.random(-1000,1000)
gsapParams.rotation=()=>gsap.utils.random(-90,90)
gsapParams.scale=()=>gsap.utils.random(0.5,1.5)
gsapParams.opacity=0}else if(elClass.includes('text-zigzag-zoom')){animateTarget.forEach((target,i)=>{gsap.from(target,{scale:(i%2===0)?0:2,opacity:0,duration:0.75,stagger:0,scrollTrigger:{trigger:el,start:"top 90%",end:"top 60%",toggleActions:`play none none none`,scrub:!1,}})});return}else if(elClass.includes('text-flip-x')){gsap.set(el,{perspective:'50px'})
gsapParams.rotateX=90;gsapParams.opacity=0}else if(elClass.includes('text-flip-y')){gsap.set(el,{perspective:'50px'})
gsapParams.rotateY=90;gsapParams.opacity=0}
if(elClass.includes('text-reveal')){gsapParams.scrollTrigger.scrub=!0}
gsap.from(animateTarget,gsapParams)};elements.each(function(i,el){applyEffects(el)});let resizeTimeout;$(window).on('resize',function(){clearTimeout(resizeTimeout);resizeTimeout=setTimeout(function(){elements.each(function(i,el){if(el.splitTextInstance){el.splitTextInstance.revert();el.splitTextInstance=null}
$(el).removeClass('text-splitted');applyEffects(el)})},300)})}
$(window).on('elementor/frontend/init',function(){elementorFrontend.hooks.addAction(`frontend/element_ready/pxl_heading.default`,function($scope){gsapTextAnimate($scope)});elementorFrontend.hooks.addAction(`frontend/element_ready/pxl_text_editor.default`,function($scope){gsapTextAnimate($scope)});elementorFrontend.hooks.addAction(`frontend/element_ready/pxl_post_title.default`,function($scope){gsapTextAnimate($scope)})})})(jQuery)
;