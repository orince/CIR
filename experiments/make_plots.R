library(tidyverse)
library(gridExtra)
library(cowplot)
library(scales)
theme_fontsize <- theme(text = element_text(size=10),
          axis.text.x = element_text(size=10), axis.text.y = element_text(size=10),
          legend.text = element_text(size=10), legend.title=element_text(size=10),
          strip.text.x = element_text(size=10), strip.text.y = element_text(size=10))

idir <- "results_rf/"
ifile.list <- list.files(idir,  pattern = "_a0\\.1\\.txt$")
print(ifile.list)
results <- do.call("rbind", lapply(ifile.list, function(ifile) {
df <- read_delim(sprintf("%s/%s", idir, ifile), delim=",", col_types=cols())
 })) %>%
    filter(n %in% c(300,500,1000,2000,3000,5000)) %>%
   filter(Symmetry %in% c(0,3,5,7,10,15,20,30))
    

df <- results %>%
    filter(Symmetry==0, Method != "CQR2"& Method != "CIR_cut"& Method != "CIR_random") %>%
    gather(`Coverage`, `Conditional coverage`, `Length`, `Length cover`, `Time`, key="key", value="value") %>%
    group_by(Method, Alpha, n, Symmetry, key) %>%
    summarise(Skewness=mean(Skewness), value.se = 2*sd(value)/sqrt(n()), value = mean(value), N=n()) %>%
    ungroup()

method.values <- c("CHR", "CQR", "DCP", "DistSplit" ,'CIR', 'CIR_rank','Oracle' )
method.labels <- c("CHR", "CQR", "DCP", "DistSplit" ,'CIR', 'CIR-FA','Oracle' )
df <- df %>%  mutate(Method = factor(Method, method.values, method.labels))
p1 <- df %>%
    filter(key %in% c("Coverage", "Conditional coverage"), Method!="Oracle") %>%
    mutate(key = factor(key, c("Coverage", "Conditional coverage"), c("Marginal", "Conditional"))) %>%
    ggplot(aes(x=n, y=value, color=Method, shape=Method)) +
    geom_hline(aes(yintercept=1-Alpha), linetype=2) +
    geom_point() +
    geom_line() +
    geom_errorbar(aes(ymin=value-value.se, ymax=value+value.se), alpha=0.5) +
    facet_grid(.~key, scales="free") +
    ylim(0.80,0.95) +
    scale_x_continuous(trans="log10") +
    guides(color=guide_legend(ncol=2)) +
    theme_bw() +
    xlab("Sample size") +
    ylab("Coverage")  +
    theme(legend.position = "none") +
    theme_fontsize
p1

df.oracle <- df %>%
    filter(Method=="Oracle", key=="Length")
length.oracle <- mean(df.oracle$value)

p2 <- df %>%
    filter(key %in% c("Length"), Method!="Oracle") %>%
    mutate(key = factor(key, c("Length", "Length cover"), c("Width", "Conditional on coverage"))) %>%
    ggplot(aes(x=n, y=value, color=Method, shape=Method)) +
    geom_hline(aes(yintercept=length.oracle), linetype=2, show.legend=FALSE) +
    geom_point() +
    geom_line() +
    geom_errorbar(aes(ymin=value-value.se, ymax=value+value.se), alpha=0.5) +
    facet_grid(.~key, scales="free") +
    ylim(3,NA) +
    scale_x_continuous(trans="log10") +
    xlab("Sample size") +
    ylab("Width") +
    theme_bw() +
    theme(legend.position = "right") +
    theme_fontsize
p2

p3 <- df %>%
    filter(key == "Time", Method != "Oracle") %>%
    ggplot(aes(x = n, y = value, color = Method, shape = Method)) +
    geom_point() +
    geom_line() +
    geom_errorbar(aes(ymin = value - value.se, ymax = value + value.se), alpha = 0.5) +
    facet_grid(. ~ key, scales = "free") +
    scale_x_continuous(trans = "log10") +
    scale_y_continuous(trans = "log10") +  # 使用对数刻度更适合展示时间数据
    xlab("Sample size") +
    ylab("Time") +
    theme_bw() +
    theme(legend.position = "right") +
    theme_fontsize
p3 <- p3  + scale_y_continuous(labels = label_number())
# 创建一个包含图例的grob
legend <- get_legend(p2 + theme(legend.position = "bottom"))
p2 <- p2 + theme(legend.position = "none")

# 组合图表
combined <- arrangeGrob(
    p1, p2, p3,
    legend,
    layout_matrix = rbind(c(1,1,2,3),
                          c(4,4,4,4)),
    widths = c(1.8, 0.1, 1.0, 1.5),
    heights = c(10, 1)
)

# 显示组合后的图表
pp <-grid.arrange(combined)
pp %>% ggsave(file="exp_synthetic_n_rf.png", height=2.2, width=9,units = "in")

# pp <- grid.arrange(p1, p2, widths=c(1.8,1.5), ncol=2)
# pp %>% ggsave(file="exp_synthetic_n.png", height=2, width=7, units = "in")

######################
df <- results %>%
    filter(n == 5000, Method != "CQR2" & Method != "CIR_cut"& Method != "CIR_random") %>%
    gather(`Coverage`, `Conditional coverage`, `Length`, `Length cover`, `Time`, key="key", value="value") %>%
    group_by(Method, Alpha, n, Symmetry, key) %>%
    summarise(Skewness=mean(Skewness), value.se = 2*sd(value)/sqrt(n()), value = mean(value)) %>%
    ungroup()
method.values <- c("CHR", "CQR", "DCP", "DistSplit" ,'CIR', 'CIR_rank' )
method.labels <- c("CHR", "CQR", "DCP", "DistSplit" ,'CIR', 'CIR-FA' )
df <- df %>%  mutate(Method = factor(Method, method.values, method.labels))
p1 <- df %>%
    filter(key %in% c("Coverage", "Conditional coverage"), Method!="Oracle") %>%
    mutate(key = factor(key, c("Coverage", "Conditional coverage"), c("Marginal", "Conditional"))) %>%
    mutate(Symmetry = Symmetry*2/100) %>%
    ggplot(aes(x=Skewness, y=value, color=Method, shape=Method)) +
    geom_hline(aes(yintercept=1-Alpha), linetype=2) +
    geom_point() +
    geom_line() +
    geom_errorbar(aes(ymin=value-value.se, ymax=value+value.se), alpha=0.5) +
    facet_grid(.~key, scales="free") +
    ylim(0.80,0.95) +
    scale_x_continuous(breaks=c(0:3), limits=c(0.5,3)) +
    theme_bw() +
    xlab("Skewness") +
    ylab("Coverage") +
    theme(legend.position = "none") +
    theme_fontsize
p1

df.oracle <- df %>%
    mutate(Method = ifelse(Method=="Oracle", NA, Method)) %>%
    filter(is.na(Method), key=="Length") %>%
    mutate(key = "Width")
length.oracle <- mean(df.oracle$value)
# 获取实际的 Method 名称
unique_methods <- unique(df$Method[df$Method != "Oracle"])
unique_methods <- method.labels 
# # 创建足够的颜色和形状
n_methods <- length(unique_methods)
colors <- scales::hue_pal()(n_methods)
shapes <- c(15:18, 3:14, 0, 1, 2)[1:n_methods]  # 这给了我们最多20个不同的形状

p2 <- df %>%
    filter(key %in% c("Length"), Method != "Oracle") %>%
    mutate(key = factor(key, c("Length", "Length cover"), c("Width", "Conditional on coverage"))) %>%
    mutate(Symmetry = Symmetry*2/100) %>%
    ggplot(aes(x = Skewness, y = value)) +
    geom_point(aes(color = Method, shape = Method)) +
    geom_line(aes(color = Method)) +
    geom_line(data = df.oracle, aes(x = Skewness, y = value), 
              color = "black", linetype = 2) +
    geom_errorbar(aes(ymin = value - value.se, ymax = value + value.se, color = Method), 
                  alpha = 0.5) +
    facet_grid(.~key, scales = "free") +
    ylim(3, NA) + 
    scale_x_continuous(breaks = c(0:3), limits = c(0.5,3)) +
    xlab("Skewness") +
    ylab("Width") +
    theme_bw() +
    theme(legend.position = "right") +
    theme_fontsize +
    scale_color_manual(values = setNames(colors, unique_methods), 
                       breaks = unique_methods) +
    scale_shape_manual(values = setNames(c(shapes, 2), c(unique_methods, NA)),
                       breaks = c(unique_methods, NA),
                       labels = c(unique_methods, "Oracle"))

p2
legend <- get_legend(p2 + theme(legend.position = "bottom"))

p3 <- df %>%
    filter(key == "Time", Method != "Oracle") %>%
    mutate(Symmetry = Symmetry*2/100) %>%
    ggplot(aes(x=Skewness, y=value, color=Method, shape=Method)) +
    geom_point() +
    geom_line() +
    geom_errorbar(aes(ymin=value-value.se, ymax=value+value.se), alpha=0.5) +
    facet_grid(.~key, scales="free") +
    scale_x_continuous(breaks=c(0:3), limits=c(0.5,3)) +
    xlab("Skewness") +
    ylab("Time") +
    theme_bw() +
    theme(legend.position = "right") +
    theme_fontsize

p3 <- p3 + scale_y_continuous(labels = label_number())   + scale_y_continuous(labels = label_number())

# 创建一个包含图例的grob

p2 <- p2 + theme(legend.position = "none")

# 组合图表
combined <- arrangeGrob(
    p1, p2, p3,
    legend,
    layout_matrix = rbind(c(1,1,2,3),
                          c(4,4,4,4)),
    widths = c(1.8, 0.1, 1.0, 1.5),
    heights = c(10, 1)
)

# 显示组合后的图表
pp <-grid.arrange(combined)
pp %>% ggsave(file="exp_synthetic_symmetry_rf.png", height=2.2, width=9,units = "in")

# # #################
# # ## Make tables ##
# # #################
# df <- results %>%
#     filter(Symmetry==0, Method != "CQR2"& Method != "CIR_cut"& Method != "CIR_random") %>%
#     gather(`Coverage`, `Conditional coverage`, `Length`, `Length cover`, `Time`, key="key", value="value") %>%
#     group_by(Method, Alpha, n, Symmetry, key) %>%
#     summarise(Skewness=mean(Skewness), value.se = 2*sd(value)/sqrt(n()), value = mean(value), N=n()) %>%
#     ungroup()

# method.values <- c("CHR", "CQR","CIR", "CIR_rank")
# method.labels <- c("CHR", "CQR","CIR", "CIR-FA" )
# df <- df %>%  mutate(Method = factor(Method, method.values, method.labels))
# df <- df %>% filter(n%in%c(500,2000,5000))
# df_clean <- na.omit(df)
# write.csv(df_clean, "synthetic_n.csv")


# #################
# ## Make tables ##
# #################
# df <- results %>%
#     filter(n == 5000, Method != "CQR2" & Method != "CIR_cut"& Method != "CIR_random") %>%
#     gather(`Coverage`, `Conditional coverage`, `Length`, `Length cover`, `Time`, key="key", value="value") %>%
#     group_by(Method, Alpha, n, Symmetry, key) %>%
#     summarise(Skewness=mean(Skewness), value.se = 2*sd(value)/sqrt(n()), value = mean(value)) %>%
#     ungroup()
# method.values <- c("CHR", "CQR",'CIR', 'CIR_rank' )
# method.labels <- c("CHR", "CQR",'CIR', 'CIR-FA' )
# df <- df %>%  mutate(Method = factor(Method, method.values, method.labels))

# df <- df %>% filter(Symmetry%in%c(3,7,30))
# df_clean <- na.omit(df)
# write.csv(df_clean, "synthetic_skew.csv")